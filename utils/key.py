brush_stroke = 'sculpt.brush_stroke'
mask_lasso_gesture = 'paint.mask_lasso_gesture'
hide_show = 'paint.hide_show'
select_lasso = 'view3d.select_lasso'
bbrush_switch = 'bbrush.bbrush_switch'
f_active = {'active': False}

view = '3D View Tool'
sculpt_modify_keymaps = {
    'Sculpt': {
        ('wm.call_panel', (('name', 'VIEW3D_PT_sculpt_context_menu'),)): {'value': "RELEASE"},
        (brush_stroke, ()): f_active,
        (brush_stroke, (('mode', 0),)): f_active,
        (brush_stroke, (('mode', 1),)): f_active,
        (brush_stroke, (('mode', 2),)): f_active,
        (mask_lasso_gesture, ()): f_active,
        (mask_lasso_gesture, (('value', 1.0),)): {'ctrl': True},
        (mask_lasso_gesture, (('value', 0.0),)): {'alt': True}, },
    f'{view}: Sculpt, Box Mask': {
        ('paint.mask_box_gesture', (('value', 1.0),)): {'ctrl': True, 'active': False},
        ('paint.mask_box_gesture', (('value', 0.0),)): {'alt': True, 'active': False}},
    f'{view}: Sculpt, Lasso Mask': {
        (mask_lasso_gesture, (('value', 1.0),)): {'ctrl': True},
        (mask_lasso_gesture, (('value', 0.0),)): {'alt': True}},
    f'{view}: Sculpt, Line Mask': {
        ('paint.mask_line_gesture', (('value', 1.0),)): {'ctrl': True},
        ('paint.mask_line_gesture', (('value', 0.0),)): {'alt': True}},
    f'{view}: Sculpt, Box Hide': {
        (hide_show, (('action', 1),)): f_active,
        (hide_show, (('action', 0),)): f_active,
        (hide_show, (('action', 1), ('area', 2))): f_active},
    f'{view}: Sculpt, Lasso Trim': {
        ('sculpt.trim_lasso_gesture', ()): {'ctrl': True, 'shift': True}},
    f'{view}: Sculpt, Box Trim': {
        ('sculpt.trim_box_gesture', ()): {'ctrl': True, 'shift': True}},
    f'{view}: Sculpt, Line Project': {
        ('sculpt.project_line_gesture', ()): {'ctrl': True, 'shift': True}},

    f'{view}: Sculpt, Mesh Filter': {
        ('sculpt.mesh_filter', ()): f_active},
    f'{view}: Sculpt, Cloth Filter': {
        ('sculpt.cloth_filter', ()): f_active},
    f'{view}: Sculpt, Color Filter': {
        ('sculpt.color_filter', ()): f_active},

    'Screen': {
        ('sculpt.project_line_gesture', ()): {'ctrl': True, 'shift': True}},
    '3D View': {
        (select_lasso, (('mode', 1),)): f_active,
        (select_lasso, (('mode', 2),)): f_active,
        (select_lasso, ()): f_active,
        ('view3d.cursor3d', ()): f_active,
        ('transform.translate', ()): f_active,
        ('emm.hdr_rotation', ()): f_active,
        ('view3d.select', ()): f_active}
}

empty_window = {'space_type': 'EMPTY', 'region_type': 'WINDOW'}
view_3d_window = {'space_type': 'VIEW_3D', 'region_type': 'WINDOW'}
empty_window_modal = {**empty_window, 'modal': True}
l_any = {'type': 'LEFTMOUSE', 'value': 'ANY', 'any': True}
bbrush_mask = 'bbrush.mask'
bbrush_sculpt = 'bbrush.bbrush_sculpt'

bbrush_key_items = (
    (bbrush_sculpt,
     {'type': 'LEFTMOUSE', 'value': 'CLICK', 'any': False},
     {'properties': [('is_click', True)]}),
    (bbrush_sculpt,
     {'type': 'LEFTMOUSE', 'value': 'CLICK_DRAG', 'any': False},
     {'properties': [('is_click', False)]}),
    (bbrush_sculpt,
     {'type': 'LEFTMOUSE', 'value': 'CLICK', 'alt': False},
     {'properties': [('is_click', True)]}),
    (bbrush_sculpt,
     {'type': 'LEFTMOUSE', 'value': 'CLICK_DRAG', 'alt': False},
     {'properties': [('is_click', False)]}),

    (bbrush_sculpt,
     {'type': 'LEFTMOUSE', 'value': 'CLICK_DRAG', 'any': False, 'alt': True},
     {'properties': [('is_click', False)]}),

    (bbrush_mask,
     {'type': 'LEFTMOUSE', 'value': 'CLICK', 'any': True, 'ctrl': True},
     {'properties': [('is_click', True)]}),
    (bbrush_mask,
     {'type': 'LEFTMOUSE', 'value': 'CLICK_DRAG', 'any': True, 'ctrl': True},
     {'properties': [('is_click', False)]}),
)

sculpt_keys_items = (
    ('View3D Rotate Modal', empty_window_modal, {'items': [
        ('CONFIRM', {'type': 'RIGHTMOUSE', 'value': 'ANY'}, None),
        ('CONFIRM', {'type': 'LEFTMOUSE', 'value': 'ANY'}, None),
        ('SWITCH_TO_ZOOM', {'type': 'LEFT_CTRL', 'value': 'ANY'}, None),
        ('AXIS_SNAP_ENABLE', {'type': 'LEFT_SHIFT', 'value': 'PRESS'}, None),
        ('AXIS_SNAP_DISABLE', {'type': 'LEFT_SHIFT', 'value': 'RELEASE'}, None), ]}),
    ('View3D Move Modal', empty_window_modal, {'items': [
        ('CONFIRM', {'type': 'RIGHTMOUSE', 'value': 'ANY'}, None),
        ('CONFIRM', {'type': 'LEFTMOUSE', 'value': 'ANY'}, None),
        ('SWITCH_TO_ZOOM', {'type': 'LEFT_ALT', 'value': 'ANY'}, None),
        ('SWITCH_TO_ZOOM', {'type': 'LEFT_CTRL', 'value': 'ANY'}, None), ]}),
    ('View3D Zoom Modal', empty_window_modal, {'items': [
        ('CONFIRM', {'type': 'RIGHTMOUSE', 'value': 'ANY'}, None),
        ('CONFIRM', {'type': 'LEFTMOUSE', 'value': 'ANY'}, None),
        ('SWITCH_TO_ROTATE', {'type': 'LEFT_CTRL', 'value': 'RELEASE'}, None),
        ('SWITCH_TO_MOVE', {'type': 'LEFT_CTRL', 'value': 'PRESS'}, None),
        ('SWITCH_TO_MOVE', {'type': 'LEFT_ALT', 'value': 'ANY'}, None), ]}),

    ('Sculpt', empty_window, {'items': [
        *bbrush_key_items,
        (bbrush_switch, {'type': 'LEFT_CTRL', 'value': 'ANY'}, None),
        (bbrush_switch, {'type': 'LEFT_ALT', 'value': 'ANY'}, None),
        (bbrush_switch, {'type': 'LEFT_SHIFT', 'value': 'ANY'}, None),
        ('object.transfer_mode',
         {'type': 'LEFTMOUSE', 'value': 'CLICK', 'alt': True}, None),
        ('view3d.rotate',
         {'type': 'RIGHTMOUSE', 'value': 'CLICK_DRAG'}, None),
        ('view3d.move',
         {'type': 'RIGHTMOUSE', 'value': 'PRESS', 'alt': True}, None),
        ('view3d.move',
         {'type': 'MIDDLEMOUSE', 'value': 'PRESS', 'alt': True}, None),
        ('view3d.zoom',
         {'type': 'RIGHTMOUSE', 'value': 'PRESS', 'ctrl': True}, None),
        ('view3d.zoom',
         {'type': 'RIGHTMOUSE', 'value': 'PRESS', 'alt': True}, None),
    ]}),
)


def keymap_register(keymap_data):
    import bpy
    wm = bpy.context.window_manager
    config = wm.keyconfigs.user

    from bl_keymap_utils.io import keymap_init_from_data
    if config:  # happens in background mode...
        for km_name, km_args, km_content in keymap_data:
            km_space_type = km_args['space_type']
            km_region_type = km_args['region_type']
            km_modal = km_args.get('modal', False)
            kmap = next(iter(
                k for k in config.keymaps
                if k.name == km_name and
                k.region_type == km_region_type and
                k.space_type == km_space_type and
                k.is_modal == km_modal
            ), None)
            if kmap is None:
                kmap = config.keymaps.new(km_name, **km_args)
            keymap_init_from_data(
                kmap, km_content['items'], is_modal=km_modal)


def __get_key_data(item):
    ke_type = item.get('type')
    ke_value = item.get('value')
    ke_any = item.get('any', False)
    ke_alt = item.get('alt', False)
    ke_ctrl = item.get('ctrl', False)
    ke_shift = item.get('shift', False)
    ke_os = item.get('oskey', False)
    ke_repeat = item.get('repeat', False)
    ke_key_modifier = item.get('key_modifier', 'NONE')

    key_ = (ke_any, ke_alt, ke_ctrl, ke_shift, ke_os) if not ke_any else (
        True, True, True, True, True)
    return ke_type, ke_value, *key_, ke_repeat, ke_key_modifier,


def __get_keydata_item(items):
    items_data = {}
    for idname, keyset, prop in items:
        prop = tuple(sorted(prop['properties'])) if prop else ()
        data_key = (idname, __get_key_data(keyset), prop)
        items_data[data_key] = None
    return items_data


def __key_to_hash_table(keymap_data):
    hash_table = {'km_name': []}
    for km_name, km_args, km_content in keymap_data:
        km_space_type = km_args['space_type']
        km_region_type = km_args['region_type']
        km_modal = km_args.get('modal', False)
        hash_key = (km_name, km_space_type, km_region_type, km_modal)
        hash_table[hash_key] = (__get_keydata_item(km_content['items']))
        hash_table['km_name'].append(km_name)
    return hash_table


def __un_key(keymap, hash_table):
    for kmi in keymap.keymap_items:
        key_ = (kmi.any, kmi.alt, kmi.ctrl, kmi.shift, kmi.oskey) if not kmi.any else (
            True, True, True, True, True)
        km_modal = keymap.is_modal
        idname = kmi.propvalue if km_modal else kmi.idname
        it_key = (kmi.type, kmi.value, *key_, kmi.repeat, kmi.key_modifier)
        prop = tuple(sorted(kmi.properties.items())
                     ) if kmi.properties else ()
        hash_ky = (idname, it_key, prop)
        if hash_ky in hash_table:
            keymap.keymap_items.remove(kmi)


def keymap_unregister(keymap_data):
    import bpy
    wm = bpy.context.window_manager
    configs = wm.keyconfigs
    keymap_hash_table = __key_to_hash_table(keymap_data)

    for config in (configs.user, configs.addon):
        for keymap in config.keymaps:
            name = keymap.name
            space = keymap.space_type
            region = keymap.region_type
            modal = keymap.is_modal
            kc_key = (name, space, region, modal)
            if kc_key in keymap_hash_table:
                __un_key(keymap,
                         keymap_hash_table[kc_key])
    del keymap_hash_table


def __set_keymap(modify, kmi):
    for key in ('shift',
                'alt',
                'ctrl',
                'value',
                'active',
                'repeat',
                'oskey',
                'type',
                ):
        if key in modify:
            setattr(kmi, key, modify.get(key))


def __modify_set_key(keymaps, keymap_hash_table, modify_bool):
    for kmi in keymaps.keymap_items:
        prop = tuple(sorted(kmi.properties.items())) if kmi.properties else ()
        hash_key = (kmi.idname, prop)
        if hash_key in keymap_hash_table:
            modify = keymap_hash_table[hash_key]
            if modify_bool:
                __set_keymap(modify, kmi)
            else:  # kmi.is_user_modified
                item = keymaps.keymap_items.from_id(
                    kmi.id)
                keymaps.restore_item_to_default(item)
                if ('active' in modify) and (not modify.get('active')):
                    kmi.active = True


def modify_keymap(keymap_hash_table, modify_bool):
    import bpy
    wm = bpy.context.window_manager
    configs = wm.keyconfigs
    if configs:  # happens in background mode...
        for config in (configs.user, configs.addon):
            for keymap in config.keymaps:
                if keymap.name in keymap_hash_table:
                    __modify_set_key(
                        keymap, keymap_hash_table[keymap.name], modify_bool)


def change_keymap(is_modify: bool):
    modify_keymap(sculpt_modify_keymaps, is_modify)


def register():
    keymap_register(sculpt_keys_items)
    change_keymap(True)


def unregister():
    keymap_unregister(sculpt_keys_items)
    change_keymap(False)
