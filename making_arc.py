import bpy

def calc_center(selectedVerts):
    median_point = bpy.context.scene.cursor.location
    #median_point.y = selectedVerts[0].co.y
    return median_point

def calc_distance(center, vertex):
    return (vertex.co - center).length

def calc_new_position(center, vertex, length):
    vec_normalized = vertex.co-center
    vec_normalized.normalize()
    return center + vec_normalized * length

def set_new_position(vertex, position):
    print (vertex.co - position)
    vertex.co = position

def make_arc():
    mode = bpy.context.active_object.mode
    bpy.ops.object.mode_set(mode='OBJECT')
    selectedVerts = [v for v in bpy.context.active_object.data.vertices if v.select]
    print("selected {} vertexes", len(selectedVerts))
    median_point = calc_center(selectedVerts)
    length = map(lambda x: calc_distance(median_point, x), selectedVerts)
    sum_length = sum(length)
    median_length = sum_length/len(selectedVerts)
    for v in  selectedVerts:
        set_new_position(v, calc_new_position(median_point, v, median_length))
    bpy.ops.object.mode_set(mode=mode)