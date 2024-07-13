bl_info = {
    "name": "Snapped Track",
    "author": "WPC",
    "version": (1, 0),
    "blender": (4, 1, 1),
    "location": "",
    "description": "",
    "category": "",
}

import bpy
from bpy.app.handlers import persistent
from mathutils import Vector
import math

def snap(value, grid):
    return round(value / grid) * grid
    
def smooth_snap(value, grid, snap_amount):
    lower_grid_point = (value // grid) * grid
    upper_grid_point = lower_grid_point + grid

    distance_to_lower = abs(value - lower_grid_point)
    distance_to_upper = abs(value - upper_grid_point)

    if distance_to_lower < distance_to_upper:
        target = lower_grid_point
    else:
        target = upper_grid_point

    new_value = value + (target - value) * snap_amount
    return new_value

def vector_snap(vector: Vector, grid: Vector):
    x = snap(vector.x, grid.x)
    y = snap(vector.y, grid.y)
    z = snap(vector.z, grid.z)
    return Vector((x, y, z))
    
def vector_smooth_snap(vector: Vector, grid: Vector, snap_amount):
    x = smooth_snap(vector.x, grid.x, snap_amount)
    y = smooth_snap(vector.y, grid.y, snap_amount)
    z = smooth_snap(vector.z, grid.z, snap_amount)
    return Vector((x, y, z))

def cartesian_to_spherical(vector: Vector):
    x = vector.x
    y = vector.y
    z = vector.z
    
    XsqPlusYsq = x**2 + y**2
    r = math.sqrt(XsqPlusYsq + z**2)
    theta = math.atan2(math.sqrt(XsqPlusYsq), z)
    phi = math.atan2(y, x)
    return Vector((r, theta, phi))

def spherical_to_cartesian(vector: Vector):
    r = vector.x
    theta = vector.y
    phi = vector.z
    
    sin_theta = math.sin(theta)
    x = r * sin_theta * math.cos(phi)
    y = r * sin_theta * math.sin(phi)
    z = r * math.cos(theta)
    return Vector((x, y, z))

def process_obj(obj, camera):
    camera_direction = Vector((0, 0, 1))

    c_r_mode = camera.rotation_mode
    camera.rotation_mode = 'QUATERNION'
    camera_direction.rotate(camera.rotation_quaternion)
    camera.rotation_mode = c_r_mode

    vec = cartesian_to_spherical(camera_direction)
    snap_value = math.pi / 16
    vec = vector_snap(vec, Vector((1, snap_value, snap_value)))
    vec = spherical_to_cartesian(vec)

    arbitrary_axis = vec
    
    camera_direction_xy = camera_direction.copy()
    camera_direction_xy.z = 0
    arbitrary_axis_xy = arbitrary_axis.copy()
    arbitrary_axis_xy.z = 0
    rot_z = arbitrary_axis_xy.rotation_difference(camera_direction_xy)
    
    arbitrary_axis_rotated = arbitrary_axis.copy()
    arbitrary_axis_rotated.rotate(rot_z)
    rot_theta = arbitrary_axis_rotated.rotation_difference(camera_direction)

    o_r_mode = obj.rotation_mode
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = rot_theta @ rot_z
    obj.rotation_mode = o_r_mode

@persistent
def process(scene):
    camera = bpy.context.scene.camera

    for obj in bpy.data.objects:
        try:
            if obj["st"] == True:
                process_obj(obj, camera)
        except KeyError:
            pass

def register():
    bpy.app.handlers.depsgraph_update_post.append(process)
    bpy.app.handlers.load_post.append(process)  #?
    bpy.app.handlers.render_pre.append(process)
    bpy.app.handlers.frame_change_pre.append(process)
    
def unregister():
    bpy.app.handlers.depsgraph_update_post.remove(process)
    bpy.app.handlers.load_post.remove(process)
    bpy.app.handlers.render_pre.remove(process)    
    bpy.app.handlers.frame_change_pre.remove(process)
    
if __name__ == "__main__":
    register()
    #unregister()