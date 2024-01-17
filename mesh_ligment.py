import bpy
import bmesh
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




class MeshToolsMakeArch(Operator):
    bl_idname = "mesh.make_arch"
    bl_label = "Make arch"
    bl_description = "Move selected vertices into an arc shape with center in 3d cursor"
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


class MeshToolsMakeLine(Operator):
    bl_idname = "mesh.make_line"
    bl_label = "Make line"
    bl_description = "Move selected vertices into a arc shape with center in 3d cursor"
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

    def invoke(self, context, event):
        # load custom settings
        # settings_load(self)
        return self.execute(context)

    def add_val(self, val, vertex_holder):
        if val in vertex_holder:
            vertex_holder[val] +=1
        else:
            vertex_holder[val] = 1

    def dec_val(self, val, vertex_holder):
        if val in vertex_holder:
            vertex_holder[val] -=1
        else:
            vertex_holder[val] = -1

    def make_line(self):
        mesh = bpy.context.active_object.data
        bm = bmesh.from_edit_mesh(mesh)

        selectedVerts = [v for v in bm.verts if v.select]
        if len(selectedVerts) < 3:
            return
        vert_holder = {}
        for vert in selectedVerts:
            self.dec_val(vert.index, vert_holder)
            for l in vert.link_edges:
                self.add_val(l.other_vert(vert).index,vert_holder)

        counter  = 0
        a = None
        b = None
        for i in vert_holder:
            if vert_holder[i] == 0:
                counter += 1
                if counter == 1:
                    a = i
                elif counter == 2:
                    b = i
                elif counter > 2:
                    self.report({'WARNING'}, "should be only single line, but got more")
                    return {'CANCELLED'}
            elif vert_holder[i] < 0:
                self.report({'WARNING'}, "should be only sigle line, but there is dot out of line")
                return {'CANCELLED'}
        if counter < 2:
            self.report({'WARNING'}, "should be only sigle line, cannot found beginig and ending")
            return {'CANCELLED'}
        print(a,b)
        mode = bpy.context.active_object.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        selectedVerts = [v for v in bpy.context.active_object.data.vertices if v.select]
        emesh = bpy.context.active_object.data
        center = emesh.vertices[a].co
        vec = emesh.vertices[b].co - center
        vec_len = vec.length_squared
        for vert in selectedVerts:
            print (vert, vert.co)
            if vert.index == a or vert.index == b:
                continue
            v1 = vert.co - center
            vproj = v1.dot(vec)/vec_len * vec
            print (vert.index, vproj)
            vert.co = center + vproj
        
        bpy.ops.object.mode_set(mode=mode)
        return{'FINISHED'}

    def execute(self, context):
        return self.make_line()




class VIEW3D_MT_MeshToolsMenu(Menu):
    bl_label = "Mesh Tools"

    def draw(self, context):
        layout = self.layout

        layout.operator("mesh.make_arch")
        layout.operator("mesh.make_line")


# define classes for registration
classes = (
    VIEW3D_MT_MeshToolsMenu,
    MeshToolsMakeArch,
    MeshToolsMakeLine
)

def menu_func(self, context):
    self.layout.menu("VIEW3D_MT_MeshToolsMenu")
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
