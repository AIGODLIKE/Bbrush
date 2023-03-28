import bpy


class UpdateProperty(PropertyGroup):

    class UpdateItems(PropertyGroup):

        class UpdateItem(PropertyGroup):

            '''
                ('',              '着色模式',     ''),
                ('WIREFRAME',        '线框',        ''),
                ('SOLID',            '实体',        ''),
                ('MATERIAL',         '预览',        ''),
                ('RENDERED',         '渲染',        ''),
                ('SCREEN',              '工作空间',     ''),
            '''

            bpy_context_mode_items = (
                ('',              '编辑',     ''),
                ('OBJECT',           '物体模式',    ''),
                ('EDIT_MESH',        '编辑网格',    ''),
                ('EDIT_CURVE',       '编辑曲线',    ''),
                ('EDIT_CURVES',      '编辑多条曲线', ''),
                ('EDIT_SURFACE',     '编辑表面',    ''),
                ('EDIT_TEXT',        '编辑文字',    ''),
                ('EDIT_ARMATURE',    '编辑骨架',    ''),
                ('EDIT_METABALL',    '编辑融球',    ''),
                ('EDIT_LATTICE',     '编辑晶格',    ''),
                ('POSE',             '姿态模式',    ''),
                ('PARTICLE',         '粒子编辑',    ''),

                ('',              'GP',     ''),
                ('PAINT_GPENCIL',    'GP绘制',      ''),
                ('EDIT_GPENCIL',     'GP编辑',      ''),
                ('SCULPT_GPENCIL',   'GP雕刻',      ''),
                ('WEIGHT_GPENCIL',   'GP权重',      ''),
                ('VERTEX_GPENCIL',   'GP顶点',      ''),

                ('',              '绘制',     ''),
                ('PAINT_WEIGHT',     '绘制权重',    ''),
                ('PAINT_VERTEX',     '绘制顶点',    ''),
                ('PAINT_TEXTURE',    '绘制纹理',    ''),

                ('',              '雕刻',     ''),
                ('SCULPT',           '雕刻模式',    ''),
                ('SCULPT_CURVES',    '雕刻曲线',    ''),

                ('',              'Misc',     ''),
                ('OTHER',              '其它',     ''),
            )

            def update_name(self, context):
                '''
                更新子项名称
                将这个名称作为
                '''

                def test_prop(prop_path, value):
                    '''
                    测试属性是否可用
                    如果可用self.is_available = True
                    '''
                    sp_ed = prop_path.split('.')[-1]
                    prop = get.property.from_path(
                        prop_path[:-len(sp_ed)-1])
                    tmp_data = get.property.from_path(prop_path)
                    typ = type(tmp_data)
                    if prop:
                        try:
                            setattr(prop, sp_ed, typ(value))
                            self.is_available = True
                        except Exception as e:

                            def draw(self, context):
                                layout = self.layout
                                layout.label(text=value_name)

                            self.value_name = value_name = str(e)
                            if self.is_enabled and self.name != 'None':
                                bpy.context.window_manager.popup_menu(
                                    draw, title='设置值错误')

                            print(f'值{value} 错误', e)

                            self.is_available = False
                        setattr(prop, sp_ed, tmp_data)
                        # print('setattr 还原', self.name, prop, sp_ed, tmp_data)
                    return self.is_available

                get = bbpy.get
                updates = get.addon.prefs().updates
                # 活动api项
                act_items = updates.update_items[updates.active_update_index]
                path = act_items.property_path

                test_prop(path, self.value)

                if self.is_available:
                    self.value_name = bpy.app.translations.pgettext(self.value)
                    self.name = self.mode
                else:
                    self.name = 'Error'

                # 测试属性是否存在多个
                is_ok = [
                    i.mode for i in act_items.mode_items if i.is_enabled and i.is_available]
                if is_ok.count(self.mode) >= 2:
                    self.is_available = False
                    self.value_name = '重复项,此项不可用!'
                    self.name = 'Error'

                act_items.name = str(set(is_ok))  # api总名称

            bpy_context_mode_items_enum = EnumProperty(items=bpy_context_mode_items,
                                                       name='模式',
                                                       update=update_name,
                                                       default='OBJECT'
                                                       )

            is_enabled: BoolProperty(
                default=True, name='是否启用此项', update=update_name)
            is_available: BoolProperty(default=False,
                                       name='是否可用',
                                       description='存储路径是否可用,如果不可用则为False,内部使用,不放置在界面上')

            mode: bpy_context_mode_items_enum

            value: StringProperty(update=update_name)
            value_name: StringProperty(
                description='name用于存mode名称,可以直接用.keys()来获取mode')

        path_name: StringProperty(
            description='name用于存mode名称,可以直接用.keys()来获取mode')
        mode_items: CollectionProperty(type=UpdateItem, name='模式更新项集合')

        def update_property(self, context):
            '''
            测试api路径是否可用,如果可用is_enabled is True 并设置 path_name 为属性的名称
            '''
            prop_path = self.property_path
            sp_ed = prop_path.split('.')[-1]

            prop = bbpy.get.property.from_path(
                prop_path[:-len(sp_ed)-1])

            if prop:
                '''
                Int
                Float
                Bool
                Enum = str
                Enum flag set{} x
                '''
                pr = prop.bl_rna.properties[sp_ed]
                self.path_name = bpy.app.translations.pgettext(pr.name)
                self.is_available = True
            else:
                self.is_available = False
                self.path_name = '错误'

        property_path: StringProperty(
            description='属性api路径', update=update_property)

        is_enabled: BoolProperty(default=True, name='是否启用此项')
        active_item_index: IntProperty(name='活动项索引值')
        is_available: BoolProperty(default=False,
                                   name='是否可用',
                                   description='存储路径是否可用,如果不可用则为False,内部使用,不放置在界面上')

    update_items: CollectionProperty(type=UpdateItems, name='更新项')
    update_is_enabled: BoolProperty(default=True, name='启用属性更新')
    active_update_index: IntProperty(name='活动项索引值')

    def _update_fps(self, value):  # 设置值
        bbpy.context.update_fps = value

    updates_fps: IntProperty(name='更新FPS',
                             min=1,
                             max=240,
                             default=10,
                             set=_update_fps,
                             get=lambda _: bbpy.context.update_fps,  # 获取直接
                             )

    split1: FloatProperty(step=0.01, min=0.01, max=0.8, default=0.5)
    split2: FloatProperty(step=0.01, min=0.01, max=0.8, default=0.5)

    class Del(bbpy.types.Operator):
        bl_idname = 'update.del_update_item'
        bl_label = '删除更新项'
        bl_options = {'REGISTER', 'UNDO'}

        update_items_index: IntProperty(default=-99,
                                        options={'SKIP_SAVE'})
        item_index: IntProperty(default=-99,
                                options={'SKIP_SAVE'})

        def invoke(self, context, event):
            updates = bbpy.get.addon.prefs().updates
            update = updates.update_items
            update_index = self.update_items_index
            index = self.item_index

            if update_index != -99 and len(update):
                mode_items = update[update_index].mode_items
                if self.item_index != -99:
                    '''
                    删除子项
                    如果索引是最后一位则-1
                    '''
                    self.set_active_index(update[update_index],
                                          'mode_items',
                                          'active_item_index')
                    mode_items.remove(index)
                else:
                    '''
                    删除属性路径项
                    如果索引是最后一位则-1
                    '''
                    self.set_active_index(updates,
                                          'update_items',
                                          'active_update_index')
                    update.remove(update_index)  # 删除更新项
            return {'FINISHED'}

    class Add(Operator):
        bl_idname = 'update.add_update_item'
        bl_label = '添加更新项'
        bl_options = {'REGISTER', 'UNDO'}

        item_index: IntProperty(default=-1, options={'SKIP_SAVE'})
        path_api: StringProperty(default='None', options={'SKIP_SAVE'})
        value: StringProperty(default='None', options={'SKIP_SAVE'})

        def draw(self, context):
            layout = self.layout
            layout.prop(self, 'path_api')
            layout.prop(self, 'value')

        def add_item(self, items):
            item = items.mode_items.add()
            item.value_name = 'None'
            item.value = self.value
            item.name = 'None'

        def execute(self, context):
            update_items = bbpy.get.addon.prefs().updates.update_items

            path_items = {i.property_path: index for index,
                          i in enumerate(update_items)}

            if self.item_index != -1:
                # 添加api子项
                items = update_items[self.item_index]
                self.add_item(items)
            else:
                if (self.path_api in path_items) and (self.path_api != 'None'):
                    # 使用api路径添加项
                    index = path_items[self.path_api]
                    items = update_items[index]
                else:
                    # 添加一个未定义的路径项
                    items = update_items.add()
                    items.path_name = '未定义'

                items.property_path = self.path_api
                if self.value:
                    self.add_item(items)

            return {'FINISHED'}

    class Import(bbpy.types.ImportPropertyOperator, ImportHelper, Operator):
        bl_idname = 'import_data.import_update_item'
        bl_label = '导入更新项'

        def set_data(self, context):
            updates = bbpy.get.addon.prefs().updates
            return bbpy.set.property.set_property_data(updates, self.data)

    class Export(bbpy.types.ExportPropertyOperator, ExportHelper, Operator):
        '''
        将更新项导出为json文件
        '''
        bl_idname = 'export_data.export_update_item'
        bl_label = '导出更新项'

        def get_data(self, context):
            updates = self.pref.updates
            return get_props_data(updates)


# end
class_tuple = (
    UpdateProperty.UpdateItems.UpdateItem,  # 子项的子项,先先注册
    UpdateProperty.UpdateItems,  # 子项,先注册
    UpdateProperty,
    UpdateProperty.Add,
    UpdateProperty.Del,
    UpdateProperty.Import,
    UpdateProperty.Export,
)

register_class, unregister_class = bpy.utils.register_classes_factory(
    class_tuple)


def register():
    register_class()


def unregister():
    unregister_class()

