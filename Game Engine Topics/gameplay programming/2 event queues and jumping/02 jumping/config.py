import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
from PIL import Image, ImageOps
from typing import TypeVar, Generic

############################## Type Aliases ###################################
#region
vec2 = list[float, float]
vec3 = list[float, float, float]
T = TypeVar("T")
#endregion
############################## Constants ######################################
#region
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

RETURN_ACTION_CONTINUE = 0
RETURN_ACTION_EXIT = 1

OBJECT_TYPE_PLAYER = 0
OBJECT_TYPE_CAMERA = 1
OBJECT_TYPE_GROUND = 2
OBJECT_TYPE_SKY = 3

PIPELINE_TYPE_SKY = 0
PIPELINE_TYPE_OBJECT = 1

END_ACTION_DESTROY = 0

#0: debug, 1: production
GAME_MODE = 0
#endregion
############################## helper functions ###############################
#region
def createShader(vertex_filepath: str, fragment_filepath: str) -> int:
    """
        Compiles and links a vertex and fragment shader.

        Parameters:

            vertex_filepath (str): the vertex shader filepath

            fragment_filepath (str): the fragment shader filepath
        
        Returns:

            int: a handle to the compiled shader
    """

    with open(vertex_filepath,'r') as f:
        vertex_src = f.readlines()

    with open(fragment_filepath,'r') as f:
        fragment_src = f.readlines()
    
    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                            compileShader(fragment_src, GL_FRAGMENT_SHADER))
    
    return shader

def load_model_from_file(
    folder: str, filename: str) -> list[float]:
    """
        Load an obj model from the given filepath.

        Parameters:

            folder (str): the path to the folder

            filename (str): the name of the file in that folder
        
        Returns:

            list[float]: the model data, flattened in a list.
    """

    v = []
    vt = []
    vn = []
    vertices = []

    with open(f"{folder}/{filename}",'r') as f:
        line = f.readline()
        while line:
            words = line.split(" ")
            match words[0]:
                case "v":
                    v.append(read_attribute_data(words))
                case "vt":
                    vt.append(read_attribute_data(words))
                case "vn":
                    vn.append(read_attribute_data(words))
                case "f":
                    read_face_data(words, v, vt, vn, vertices)
            line = f.readline()
    
    return vertices

def read_attribute_data(words: list[str]) -> vec2 | vec3:
    """
        Read an attribute description and return its contents in a list

        Parameters:

            words (list[str]): the values to read for the attribute.
        
        Returns:

            vec2 | vec3: the parsed attributes
    """

    return [float(words[i + 1]) for i in range(len(words) - 1)]

def read_face_data(
    words: list[str], v: list[vec3], 
    vt: list[vec2], vn: list[vec3], 
    vertices: list[float]) -> None:
    """
        Read a face description.

        Parameters:

            words (list[str]): the corner descriptions.

            v (list[vec3]): the vertex position list

            vt (list[vec2]): the texcoord list

            vn (list[vec3]): the normal list

            vertices (list[float]): the result list

    """
    
    triangles_in_face = len(words) - 3

    for i in range(triangles_in_face):
        read_corner(words[1], v, vt, vn, vertices)
        read_corner(words[i + 2], v, vt, vn, vertices)
        read_corner(words[i + 3], v, vt, vn, vertices)

def read_corner(
    description: str, 
    v: list[vec3], vt: list[vec2], 
    vn: list[vec3], vertices: list[float]) -> None:
    """
        Read a description of a corner, adding its contents to the
        vertices.

        Parameters:

            words (list[str]): the corner descriptions.

            v (list[vec3]): the vertex position list

            vt (list[vec2]): the texcoord list

            vn (list[vec3]): the normal list

            vertices (list[float]): the result list
    """

    v_vt_vn = description.split("/")

    for x in v[int(v_vt_vn[0]) - 1]:
        vertices.append(x)
    for x in vn[int(v_vt_vn[2]) - 1]:
        vertices.append(x)
#endregion
###############################################################################