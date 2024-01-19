import bpy
from bpy.types import Operator

bl_info = {
    "name": "Make arch",
    "author": "idimus (Smbat Makiyan)",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Edit Tab / Edit Mode Context Menu/ Make arch",
    "warning": "",
    "description": "Make arch tool",
    "doc_url": "",
    "category": "Mesh",
}

class MeshToolsMakeArch(Operator):
    bl_idname = "mesh.make_arch"
    bl_label = "Make arch"
    bl_description = "Shape selected vertices into an arch shape with center in 3d cursor"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return(ob and ob.type == 'MESH' and context.mode == 'EDIT_MESH')

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
        print ("selected {} vertexes", len(selectedVerts))
        if len(selectedVerts) < 2:
            self.report({'WARNING'}, "too few points, should be at least 2")
            return {'CANCELLED'}
        median_point = self.calc_center(selectedVerts)
        length = map(lambda x: self.calc_distance(median_point, x), selectedVerts)
        sum_length = sum(length)
        median_length = sum_length/len(selectedVerts)
        for v in  selectedVerts:
            self.set_new_position(v, self.calc_new_position(median_point, v, median_length))
        bpy.ops.object.mode_set(mode=mode)
        return{'FINISHED'}


    def execute(self, context):
        return self.make_arc()


def menu_func(self, context):
    self.layout.operator("mesh.make_arch")

# registering and menu integration
def register():
    bpy.utils.register_class(MeshToolsMakeArch)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.prepend(menu_func)

# unregistering and removing menus
def unregister():
    bpy.utils.unregister_class(MeshToolsMakeArch)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(menu_func)

if __name__ == "__main__":
    register()
