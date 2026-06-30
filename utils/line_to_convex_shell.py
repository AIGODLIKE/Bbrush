import bpy
from mathutils import Vector
from mathutils import geometry


def to_vector(data):
    return [Vector(i).freeze() for i in data]


def get_all_intersect_pos(pos):
    po_len = pos.__len__()
    indices_list = [(i - 1, i) for i in range(1, po_len)] + [
        (0, po_len - 1)]
    tmp_dict = {'intersect': {}, 'line': {i: [] for i in indices_list}}
    while indices_list:
        cur_line = indices_list.pop()
        if cur_line not in tmp_dict['line']:
            tmp_dict['line'][cur_line] = [pos[cur_line[0]],
                                          pos[cur_line[1]]]
        for line in indices_list:
            if line not in tmp_dict['line']:
                tmp_dict['line'][line] = [pos[line[0]], pos[line[1]]]

            get_int = geometry.intersect_line_line_2d(
                pos[cur_line[0]],
                pos[cur_line[1]],
                pos[line[0]],
                pos[line[1]],
            )
            if get_int:
                get_int = get_int.freeze()
                tmp_dict['intersect'][get_int] = [cur_line, line]
                tmp_dict['line'][line].append(get_int)
                tmp_dict['line'][cur_line].append(get_int)
    return tmp_dict


def to_left(startpoint, endpoint, co) -> bool:
    """Return True if co is left of the directed segment startpoint -> endpoint (2D, z=0)."""
    line1 = (endpoint - startpoint).to_3d()
    line2 = (co - startpoint).to_3d()
    return line1.cross(line2)[-1] > 0


def find_closet(point_list, src_point):
    """Return the closest point in point_list to src_point."""
    min_dist = 9999999999999
    find_point = None
    for v in point_list:
        if v == src_point:
            continue
        d = (v - src_point).magnitude
        if d < min_dist:
            find_point = v
            min_dist = d
    return find_point


def line_to_convex_shell(pos, link=False):
    """Extract the outer boundary polygon from a self-intersecting polyline."""
    # [v1, v2, v3, v1]
    pos = to_vector(pos)
    pos_neibor = {
        k: [
            i - 1 if (i - 1) != -1 else len(pos) - 1, i + 1 if
            (i + 1) != len(pos) else 0
        ]
        for i, k in enumerate(pos)
    }

    convex_hull_2d = geometry.convex_hull_2d(pos)
    int_dict = get_all_intersect_pos(pos.copy())
    from_idx = convex_hull_2d[0]
    from_point = pos[from_idx]
    origin_point = from_point

    # Assume hull walk follows endpoint segments
    end1_idx, end2_idx = pos_neibor[from_point]
    # Pick end1_idx as the next start vertex
    if to_left(from_point, pos[end1_idx], pos[end2_idx]):
        end1_idx = end2_idx

    # Current edge pair index
    pair = (end1_idx, from_idx) if end1_idx < from_idx else \
        (from_idx, end1_idx)

    # First step: if target is not an endpoint, pick nearest left intersection
    if len(int_dict['line'][pair]) > 2:
        # Nearest intersection on the left side
        find_point = find_closet(int_dict['line'][pair], from_point)
        to_point = find_point
        try:
            from_idx = pos.index(find_point)
        except Exception as e:
            print(e)
            from_idx = -9999
    else:
        from_idx = end1_idx
        to_point = pos[end1_idx]

    circle = []
    counter = 0
    while True:
        circle.append(from_point)
        if (len(int_dict['line'][pair]) == 2) or (-1 < from_idx < len(pos)):
            # Endpoint: follow the adjacent edge
            from_point = to_point
            end1_idx, end2_idx = pos_neibor[from_point]

            pair1 = (end1_idx, from_idx) if end1_idx < from_idx else \
                (from_idx, end1_idx)
            pair2 = (end2_idx, from_idx) if end2_idx < from_idx else \
                (from_idx, end2_idx)

            pair = (pair2 if pair1 == pair else pair1)
            # Intersection on edge vs endpoint vertex
            find_point = find_closet(int_dict['line'][pair], from_point)
            if len(int_dict['line'][pair]) > 2:
                # Intersection point
                to_point = find_point
                from_idx = -9999
            else:
                # Endpoint vertex
                from_idx = pair[0] if pair[1] == from_idx else pair[1]
                to_point = pos[from_idx]
        else:
            # Non-endpoint: collect intersections on the active edge pair
            pair1, pair2 = int_dict['intersect'][to_point]
            pair = (pair2 if pair1 == pair else pair1)

            # Keep points left of the current segment
            left_point = []
            for v in int_dict['line'][pair]:
                if to_left(from_point, to_point, v):
                    # On the left
                    left_point.append(v)
            # Nearest left intersection ahead
            find_point = find_closet(left_point, to_point)
            from_point, to_point = to_point, find_point
            try:
                from_idx = pos.index(find_point)
            except IndexError as e:
                from_idx = -9999
        # Loop closed back to origin
        if to_point == origin_point:
            circle.append(from_point)
            circle.append(origin_point)
            # Closed boundary found
            break
        counter += 1
        if counter > len(pos) * 12:
            break
    if link:
        return circle, circle_test(circle, True)
    return circle


def circle_test(circle, new_obj=False):
    """Debug helper: build a mesh from the boundary loop."""
    if 'sss' in bpy.data.meshes:
        bpy.data.meshes.remove(bpy.data.meshes['sss'])
    me = bpy.data.meshes.new("sss")
    me.from_pydata(vertices=[v.to_3d() / 100 for v in circle],
                   edges=[(i, i + 1) for i in range(len(circle) - 1)],
                   faces=[])
    me.update()

    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.0001)
    bmesh.ops.triangle_fill(bm, edges=bm.edges[:])
    bm.to_mesh(me)
    bm.free()
    if new_obj:
        if "sss" not in bpy.data.objects:
            o = bpy.data.objects.new("sss", object_data=me)
        else:
            o = bpy.data.objects['sss']
            o.data = me
        if o.name not in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.link(o)

    return (i.vertices[:] for i in me.polygons)
