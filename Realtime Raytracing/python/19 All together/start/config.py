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

SPHERE_STRIDE                   = 12
SPHERE_ATTRIBUTE_X              = 0
SPHERE_ATTRIBUTE_Y              = 1
SPHERE_ATTRIBUTE_Z              = 2
SPHERE_ATTRIBUTE_RADIUS         = 3
SPHERE_ATTRIBUTE_R              = 4
SPHERE_ATTRIBUTE_G              = 5
SPHERE_ATTRIBUTE_B              = 6
SPHERE_ATTRIBUTE_REFLECTANCE    = 7
SPHERE_ATTRIBUTE_ETA            = 8

NODE_STRIDE                 = 8
NODE_ATTRIBUTE_MIN_X        = 0
NODE_ATTRIBUTE_MIN_Y        = 1
NODE_ATTRIBUTE_MIN_Z        = 2
NODE_ATTRIBUTE_SPHERE_COUNT = 3
NODE_ATTRIBUTE_MAX_X        = 4
NODE_ATTRIBUTE_MAX_Y        = 5
NODE_ATTRIBUTE_MAX_Z        = 6
NODE_ATTRIBUTE_CONTENTS     = 7