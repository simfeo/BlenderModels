import bpy
import mathutils
from bpy.types import Operator
from bpy.props import (
        FloatProperty,
        EnumProperty,
)

bl_info = {
    "name": "Make arch",
    "author": "idimus (Smbat Makiyan)",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Edit Tab / Edit Mode Context Menu/ Make arch",
    "warning": "",
    "description": "Make arch tool",
    "doc_url": "",
    "category": "Mesh",
}

def in_object_mode(func):
    def wrapper(*args, **kwargs):
        if [bpy.context.active_object] != bpy.context.selected_objects:
            for i in bpy.context.selected_objects:
                i.select_set(False)
            bpy.context.active_object.select_set(True)
            
        mode = bpy.context.active_object.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        object_initial_loc = bpy.context.active_object.location.copy()
        cursor_inital_loc = bpy.context.scene.cursor.location.copy()
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        result = func(*args, **kwargs)
        
        bpy.context.scene.cursor.location = object_initial_loc
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.context.scene.cursor.location = cursor_inital_loc
        bpy.ops.object.mode_set(mode=mode)
        return result
    return wrapper

class MeshToolsMakeArch(Operator):
    bl_idname = "mesh.make_arch"
    bl_label = "Make arch"
    bl_description = "Shape selected vertices into an arch shape with center in 3d cursor"
    bl_options = {'REGISTER', 'UNDO'}

    radius: FloatProperty(
        name="Radius",
        description="Radius of arch curvature",
        default=0.0,
        soft_min=-1024.0,
        soft_max=1024.0
        )
    
    lock_axis: EnumProperty(
        name="LockAxis",
        items=(("none", "None", "Do not lock axis"),
               ("screen", "Screen", "Lock by current screen rotation"),
               ("x", "X", "Lock X"),
               ("y", "Y", "Lock Y"),
               ("z", "Z", "Lock Z"),
              ),
        description="Lock axis for radius",
        default='none'
        )

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return(ob and ob.type == 'MESH' and context.mode == 'EDIT_MESH')

    def invoke(self, context, event):
        self.radius = 0.0
        return self.execute(context)

    def calc_distance(self, vertex):
        return (vertex.co).length

    def calc_new_position(self, vertex, length):
        vec_normalized = vertex.co
        vec_normalized.normalize()
        return vec_normalized * length

    def set_new_position(self, vertex, position):
        vertex.co = position

    def make_arc_simple(self, selectedVerts):
        if self.radius == 0.0 or self.radius == 0:
            length = map(lambda x: self.calc_distance(x), selectedVerts)
            sum_length = sum(length)
            self.radius = sum_length/len(selectedVerts)

        for v in  selectedVerts:
            self.set_new_position(v, self.calc_new_position(v, self.radius))
    
    def calc_distance_normal(self, vertex, normal):
        # proj p = P*Q/Q.length x Q
        # where Q is normal and unit vector, so Q.lenght == 1
        proj = normal * (vertex.co@normal)
        return proj.length
    
    def calc_new_position_normal(self, vertex, length, normal):
        vec_normalized = vertex.co
        proj = normal * (vertex.co@normal)
        vec_normalized = vec_normalized - proj
        vec_normalized.normalize()
        vec_normalized = vec_normalized * length
        return vec_normalized + proj, proj
    
    # normal is normal vector for plane
    def make_arc_normal(self, selectedVerts, normal):
        if self.radius == 0.0 or self.radius == 0:
            length = map(lambda x: self.calc_distance_normal(x, normal), selectedVerts)
            sum_length = sum(length)
            self.radius = sum_length/len(selectedVerts)
            
        nn = []
        for v in  selectedVerts:
            pos, proj = self.calc_new_position_normal(v, self.radius, normal)
            nn.append(proj)
            self.set_new_position(v, pos)
        
        # mm = MeshToolsMakeArch.create_pointed_mesh("mmmm", nn)
        # bpy.context.collection.objects.link(mm)
            
            
    # def create_pointed_mesh(ob_name, coords, edges=[], faces=[]):
    #     me = bpy.data.meshes.new(ob_name + "Mesh")
    #     ob = bpy.data.objects.new(ob_name, me)
    #     me.from_pydata(coords, edges, faces)
    #     ob.show_name = True
    #     me.update()
    #     return ob

    @in_object_mode
    def make_arc(self):
        selectedVerts = [v for v in bpy.context.active_object.data.vertices if v.select]
        # print ("selected {} vertexes", len(selectedVerts))
        if len(selectedVerts) < 2:
            self.report({'WARNING'}, "too few points, should be at least 2")
            return {'CANCELLED'}
        
        if self.lock_axis == "none":
            self.make_arc_simple(selectedVerts)
        else:
            # 1,0,0
            # <Vector (0.0000, 1.0000, 0.0000)> <Quaternion (w=0.5000, x=0.5000, y=0.5000, z=0.5000)> x
            # <Vector (-1.0000, 0.0000, -0.0000)> <Quaternion (w=0.0000, x=-0.0000, y=0.7071, z=0.7071)> y 
            # <Vector (1.0000, 0.0000, 0.0000)> <Quaternion (w=1.0000, x=-0.0000, y=-0.0000, z=-0.0000)> z
            # 0,0,1
            # <Vector (1.0000, 0.0000, 0.0000)> <Quaternion (w=0.5000, x=0.5000, y=0.5000, z=0.5000)> x
            # <Vector (0.0000, 1.0000, 0.0000)> <Quaternion (w=0.0000, x=-0.0000, y=0.7071, z=0.7071)> y
            # <Vector (0.0000, 0.0000, 1.0000)> <Quaternion (w=1.0000, x=-0.0000, y=-0.0000, z=-0.0000)> z
            vec = mathutils.Vector((0,0,1))
            if self.lock_axis == "screen":
                view_quat = bpy.context.region_data.view_rotation
                vec = mathutils.Vector((0,0,1))
                vec = view_quat@vec
                # print(view_quat@vec, view_quat)
            elif self.lock_axis == "x":
                vec = mathutils.Vector((1,0,0))
            elif self.lock_axis == "y":
                vec = mathutils.Vector((0,1,0))
            elif self.lock_axis == "z":
                vec = mathutils.Vector((0,0,1))

            self.make_arc_normal(selectedVerts, vec)


        return{'FINISHED'}

    def execute(self, context):
        return self.make_arc()


def menu_func(self, context):
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.operator(MeshToolsMakeArch.bl_idname)

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
