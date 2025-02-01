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

DATA_TYPE_SPHERE = np.dtype({
    'names': [
        'x','y','z','radius', 
        'r', 'g', 'b', 'reflectance', 
        'eta'],
    'formats': [
        np.float32, np.float32, np.float32, np.float32, 
        np.float32, np.float32, np.float32, np.float32, 
        np.float32],
    'offsets': [
        0, 4, 8, 12, 
        16, 20, 24, 28, 
        32],
    'itemsize': 48})

DATA_TYPE_NODE = np.dtype({
    'names': [
        'min_x','min_y','min_z','sphere_count', 
        'max_x', 'max_y', 'max_z', 'contents'],
    'formats': [
        np.float32, np.float32, np.float32, np.float32, 
        np.float32, np.float32, np.float32, np.float32],
    'offsets': [
        0, 4, 8, 12, 
        16, 20, 24, 28],
    'itemsize': 32})