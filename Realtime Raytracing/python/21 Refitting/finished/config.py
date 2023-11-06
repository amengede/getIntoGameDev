import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
import time
from PIL import Image, ImageOps
from numba import njit

np.random.seed(0)

data_type_sphere = np.dtype({
    'names':   [       'x',        'y',        'z',   'radius',       'vx',       'vy',       'vz', 'material'], 
    'formats': [np.float32, np.float32, np.float32, np.float32, np.float32, np.float32, np.float32,  np.uint32],
    'offsets': [         0,          4,          8,         12,         16,         20,         24,         28],
    'itemsize': 32})

data_type_material = np.dtype({
    'names':   [       'r',        'g',        'b', 'reflectance',      'eta'], 
    'formats': [np.float32, np.float32, np.float32,    np.float32, np.float32],
    'offsets': [         0,          4,          8,            12,         16],
    'itemsize': 32})

data_type_bvh_node = np.dtype({
    'names':   [   'min_x',    'min_y',    'min_z', 'sphere_count',    'max_x',    'max_y',    'max_z', 'contents'], 
    'formats': [np.float32, np.float32, np.float32,       np.int32, np.float32, np.float32, np.float32,   np.int32],
    'offsets': [         0,          4,          8,             12,         16,         20,         24,         28],
    'itemsize': 32})