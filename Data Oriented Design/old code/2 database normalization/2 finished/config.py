############################## Imports   ######################################
#region
import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
from PIL import Image
from numba import njit
#endregion
############################## Constants ######################################
#region
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

PIPELINE_TYPE = {
    "STANDARD": 0,
    "EMISSIVE": 1,
}

ENTITY_TYPE = {
    "CUBE": 0,
    "POINTLIGHT": 1,
}

COMPONENT_TYPE = {
    "DEFAULT": 0,
    "TRANSFORM": 1,
    "COLOR": 2,
}
#endregion
###############################################################################