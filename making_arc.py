import bpy
from bpy.types import (
        Operator,
        Menu,
        Panel,
        PropertyGroup,
        AddonPreferences,
        )
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        )

bl_info = {
    "name": "Vertex aligment",
    "author": "idimus (Smbat Makiyan)",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Edit Tab / Edit Mode Context Menu",
    "warning": "",
    "description": "Vertex aligment toolkit",
    "doc_url": "",
    "category": "Mesh",
}


# class MeshToolsMakeArch(bpy.types.Operator):
#     bl_idname = "object.my_addon"
#     bl_label = "My Addon"

#     def execute(self, context):
#         layout = self.layout
#         layout.operator_context = 'INVOKE_DEFAULT'
#         layout.operator("object.my_addon")
#         return {'FINISHED'}



class MeshToolsMakeArch(Operator):
    bl_idname = "mesh.make_arch"
    bl_label = "Make Arch"
    bl_description = "Move selected vertices into a circle shape"
    bl_options = {'REGISTER', 'UNDO'}

    custom_radius: BoolProperty(
        name="Align",
        description="Force a custom radius",
        default=False
        )

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return(ob and ob.type == 'MESH' and context.mode == 'EDIT_MESH')

    def draw(self, context):
        layout = self.layout
        col = layout.column()


        row = col.row(align=True)
        row.prop(self, "custom_radius")
        row_right = row.row(align=True)
        row_right.active = self.custom_radius
        row_right.prop(self, "radius", text="")
        

    def invoke(self, context, event):
        # load custom settings
        # settings_load(self)
        return self.execute(context)

    def calc_center(self, selectedVerts):
        median_point = bpy.context.scene.cursor.location
        #median_point.y = selectedVerts[0].co.y
        return median_point

    def calc_distance(self, center, vertex):
        return (vertex.co - center).length

    def calc_new_position(self, center, vertex, length):
        vec_normalized = vertex.co-center
        vec_normalized.normalize()
        return center + vec_normalized * length

    def set_new_position(self, vertex, position):
        print (vertex.co - position)
        vertex.co = position

    def make_arc(self):
        mode = bpy.context.active_object.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        selectedVerts = [v for v in bpy.context.active_object.data.vertices if v.select]
        # print ("selected {} vertexes", len(selectedVerts))
        median_point = self.calc_center(selectedVerts)
        length = map(lambda x: self.calc_distance(median_point, x), selectedVerts)
        sum_length = sum(length)
        median_length = sum_length/len(selectedVerts)
        for v in  selectedVerts:
            self.set_new_position(v, self.calc_new_position(median_point, v, median_length))
        bpy.ops.object.mode_set(mode=mode)

    def execute(self, context):
        self.make_arc()

        return{'FINISHED'}


class MeshToolsMenu(Menu):
    bl_label = "Mesh Tools"

    def draw(self, context):
        layout = self.layout

        layout.operator("mesh.make_arch")


# define classes for registration
classes = (
    MeshToolsMenu,
    MeshToolsMakeArch
)

def menu_func(self, context):
    self.layout.menu("MeshToolsMenu")
    self.layout.separator()

# registering and menu integration
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.prepend(menu_func)



# unregistering and removing menus
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(menu_func)



if __name__ == "__main__":
    register()
