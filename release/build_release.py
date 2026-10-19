"""Bbrush 发布打包脚本.

用法:
  python release/build_release.py                       打包当前版本 -> dist/Bbrush.zip (GitHub Release 附件名)
  python release/build_release.py --bump patch          版本号 +0.0.1 (同时改 __init__.py 与 blender_manifest.toml), 不打包
  python release/build_release.py --set-version 1.5.2   指定版本号, 不打包
  python release/build_release.py --blender "C:/.../blender.exe"   打包后用 Blender 校验并做启用冒烟测试 (可重复指定)
  python release/build_release.py --list                只列出将要打包的文件

打包内容以 git 跟踪的文件为白名单, 工作区有未提交改动时拒绝打包(除非 --allow-dirty).
冒烟测试使用临时的 BLENDER_USER_SCRIPTS / BLENDER_USER_CONFIG, 不会改动本机的 Blender 偏好设置.
本脚本不会提交、打标签或上传任何内容.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import os
import py_compile
import re
import subprocess
import sys
import tempfile
import warnings
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "Bbrush"
MANIFEST = ROOT / "blender_manifest.toml"
INIT = ROOT / "__init__.py"

EXCLUDED_ROOTS = {"release", "dist", "tests", ".idea", ".vs", ".vscode", ".cursor", ".claude", ".git", ".Bbrush"}
EXCLUDED_FILES = {".gitignore", ".gitattributes", ".editorconfig", "README.md", "AGENTS.md", "CLAUDE.md"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".blend1", ".log", ".zip"}
REQUIRED_FILES = ("__init__.py", "blender_manifest.toml", "debug.py", "src/view_navigation/Default.png")

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
INIT_VERSION_RE = re.compile(r'("version"\s*:\s*)\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)')
MANIFEST_VERSION_RE = re.compile(r'^(version\s*=\s*)"[^"]*"', re.M)


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=True, timeout=60)
    return result.stdout.strip()


def init_version() -> str:
    tree = ast.parse(INIT.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "bl_info" for t in node.targets):
            version = ast.literal_eval(node.value)["version"]
            return ".".join(str(v) for v in version)
    raise RuntimeError("__init__.py 中没有 bl_info")


def manifest_version() -> str:
    match = MANIFEST_VERSION_RE.search(MANIFEST.read_text(encoding="utf-8"))
    if match is None:
        raise RuntimeError("blender_manifest.toml 中没有 version")
    return match.group(0).split('"')[1]


def check_version() -> str:
    a, b = init_version(), manifest_version()
    if a != b:
        raise RuntimeError(f"版本号不一致: __init__.py={a}, blender_manifest.toml={b}")
    return a


def set_version(version: str) -> None:
    if not VERSION_RE.match(version):
        raise ValueError(f"版本号格式应为 X.Y.Z: {version}")
    major, minor, patch = version.split(".")
    for path, pattern, repl in (
            (INIT, INIT_VERSION_RE, rf"\g<1>({major}, {minor}, {patch})"),
            (MANIFEST, MANIFEST_VERSION_RE, rf'\g<1>"{version}"'),
    ):
        text = path.read_text(encoding="utf-8")
        new, count = pattern.subn(repl, text, count=1)
        if count != 1:
            raise RuntimeError(f"未能在 {path.name} 中替换版本号")
        path.write_bytes(new.encode("utf-8"))
    print(f"版本号已改为 {version} (未提交)")


def bump_version(part: str) -> None:
    major, minor, patch = (int(v) for v in check_version().split("."))
    if part == "major":
        major, minor, patch = major + 1, 0, 0
    elif part == "minor":
        minor, patch = minor + 1, 0
    else:
        patch += 1
    set_version(f"{major}.{minor}.{patch}")


def runtime_files() -> list[str]:
    files = []
    for rel in git("ls-files", "-z").split("\0"):
        if not rel:
            continue
        parts = rel.split("/")
        if parts[0] in EXCLUDED_ROOTS or (len(parts) == 1 and parts[0] in EXCLUDED_FILES):
            continue
        if "__pycache__" in parts or Path(rel).suffix.lower() in EXCLUDED_SUFFIXES:
            continue
        if not (ROOT / rel).is_file():
            raise RuntimeError(f"git 跟踪的文件在工作区中不存在: {rel}")
        files.append(rel)
    return sorted(files)


def check_sources(files: list[str]) -> None:
    errors = []
    with tempfile.TemporaryDirectory() as tmp, warnings.catch_warnings():
        warnings.simplefilter("error", SyntaxWarning)
        for rel in files:
            if rel.endswith(".py"):
                try:
                    py_compile.compile(str(ROOT / rel), cfile=os.path.join(tmp, "c.pyc"), doraise=True)
                except py_compile.PyCompileError as e:
                    errors.append(str(e))
    if errors:
        raise RuntimeError("源码编译失败:\n" + "\n".join(errors))


def check_dirty(allow_dirty: bool) -> str:
    status = git("status", "--porcelain", "--untracked-files=all")
    if status and not allow_dirty:
        raise RuntimeError("工作区有未提交的改动, 请先提交后再打包 (内部测试可加 --allow-dirty):\n" + status)
    return status


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_archive(output: Path, files: list[str]) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for rel in files:
            archive.write(ROOT / rel, f"{PACKAGE_NAME}/{rel}")
    with zipfile.ZipFile(output) as archive:
        names = archive.namelist()
        if archive.testzip() is not None:
            raise RuntimeError("压缩包 CRC 校验失败")
    for name in names:
        rel = name[len(PACKAGE_NAME) + 1:]
        if not name.startswith(PACKAGE_NAME + "/") or ".." in rel.split("/"):
            raise RuntimeError(f"非法的压缩包成员: {name}")
    for required in REQUIRED_FILES:
        if f"{PACKAGE_NAME}/{required}" not in names:
            raise RuntimeError(f"压缩包缺少 {required}")
    return output


SMOKE_SCRIPT = r"""
import sys, bpy
bpy.context.preferences.use_preferences_save = False
name = sys.argv[sys.argv.index("--") + 1]
bpy.ops.preferences.addon_enable(module=name)
ok = name in bpy.context.preferences.addons
kc = bpy.context.window_manager.keyconfigs.addon
items = sum(len(km.keymap_items) for km in kc.keymaps)
bpy.ops.preferences.addon_disable(module=name)
ok = ok and name not in bpy.context.preferences.addons
print("SMOKE_RESULT", "OK" if ok else "FAIL", "keymap_items=%d" % items)
"""


def blender_check(blender: str, archive: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        env = dict(os.environ, BLENDER_USER_SCRIPTS=str(tmp / "scripts"), BLENDER_USER_CONFIG=str(tmp / "config"))

        result = subprocess.run([blender, "-b", "--factory-startup", "--command", "extension", "validate", str(archive)],
                                text=True, capture_output=True, timeout=300, env=env)
        print(result.stdout.strip() or result.stderr.strip())
        if result.returncode != 0:
            raise RuntimeError("Blender extension validate 失败")

        addons = tmp / "scripts" / "addons"
        addons.mkdir(parents=True)
        with zipfile.ZipFile(archive) as z:
            z.extractall(addons)
        script = tmp / "smoke.py"
        script.write_text(SMOKE_SCRIPT, encoding="utf-8")
        result = subprocess.run([blender, "-b", "--factory-startup", "--python", str(script), "--", PACKAGE_NAME],
                                text=True, capture_output=True, timeout=300, env=env)
        output = result.stdout + result.stderr
        smoke = [line for line in output.splitlines() if line.startswith("SMOKE_RESULT")]
        errors = [line for line in output.splitlines() if "Traceback" in line or "Error" in line]
        print("\n".join(smoke + errors))
        if not smoke or "OK" not in smoke[0] or errors:
            print(output)
            raise RuntimeError("Blender 启用冒烟测试失败")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--bump", choices=("major", "minor", "patch"), help="提升版本号后退出")
    group.add_argument("--set-version", help="设置版本号后退出")
    group.add_argument("--list", action="store_true", help="只列出将要打包的文件")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--allow-dirty", action="store_true", help="允许在有未提交改动时打包(文件名带 -dirty)")
    parser.add_argument("--blender", action="append", default=[],
                        help="Blender 可执行文件路径, 可重复指定以测试多个版本")
    args = parser.parse_args(argv)

    if args.bump:
        bump_version(args.bump)
        return 0
    if args.set_version:
        set_version(args.set_version)
        return 0

    version = check_version()
    files = runtime_files()
    if args.list:
        print("\n".join(files))
        return 0

    status = check_dirty(args.allow_dirty)
    check_sources(files)
    label = PACKAGE_NAME + ("-dirty" if status else "")
    archive = build_archive(args.output_dir.resolve() / f"{label}.zip", files)
    for blender in args.blender:
        print(f"== {blender}")
        blender_check(blender, archive)
    digest = sha256(archive)
    archive.with_name(archive.name + ".sha256").write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    print(f"version: {version}")
    print(f"commit: {git('rev-parse', '--short', 'HEAD')}{' (dirty)' if status else ''}")
    print(f"files : {len(files)}")
    print(f"sha256: {digest}")
    print(archive)
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError, subprocess.CalledProcessError) as e:
        print(f"错误: {e}", file=sys.stderr)
        raise SystemExit(1)
