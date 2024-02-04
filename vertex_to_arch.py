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

def in_object_mode(func):
    def wrapper(*args, **kwargs):
        mode = bpy.context.active_object.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        result = func(*args, **kwargs)
        bpy.ops.object.mode_set(mode=mode)
        return result
    return wrapper

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

    def calc_distance(self, vertex):
        return (vertex.co).length

    def calc_new_position(self, vertex, length):
        vec_normalized = vertex.co
        vec_normalized.normalize()
        return vec_normalized * length

    def set_new_position(self, vertex, position):
        vertex.co = position

    @in_object_mode
    def make_arc(self):
        object_initial_loc = bpy.context.active_object.location.copy()
        cursor_inital_loc = bpy.context.scene.cursor.location.copy()
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        selectedVerts = [v for v in bpy.context.active_object.data.vertices if v.select]
        print ("selected {} vertexes", len(selectedVerts))
        if len(selectedVerts) < 2:
            self.report({'WARNING'}, "too few points, should be at least 2")
            return {'CANCELLED'}
        
        length = map(lambda x: self.calc_distance(x), selectedVerts)
        sum_length = sum(length)
        median_length = sum_length/len(selectedVerts)

        for v in  selectedVerts:
            self.set_new_position(v, self.calc_new_position(v, median_length))

        bpy.context.scene.cursor.location = object_initial_loc
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.context.scene.cursor.location = cursor_inital_loc

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
