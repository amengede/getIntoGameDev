import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
import ctypes
from PIL import Image, ImageOps
import math
from numba import njit

vec = list[float]

DATA_TYPE_PARTICLE = np.dtype({
    'names': [
         'x',  'y',  'z',
        'vx', 'vy', 'vz'],
    'formats': [
        np.float32, np.float32, np.float32,
        np.float32, np.float32, np.float32],
    'offsets': [
         0,  4,  8, 
        12, 16, 20],
    'itemsize': 24})
