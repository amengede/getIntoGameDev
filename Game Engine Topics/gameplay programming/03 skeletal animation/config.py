import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
from PIL import Image, ImageOps
from typing import TypeVar, Generic
import json
import base64
import struct
from collections.abc import Callable

#region Type Aliases
vec2 = list[float, float]
vec3 = list[float, float, float]
T = TypeVar("T")
#endregion
#region Constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

RETURN_ACTION_CONTINUE = 0
RETURN_ACTION_EXIT = 1

OBJECT_TYPE_PLAYER = 0
OBJECT_TYPE_CAMERA = 1
OBJECT_TYPE_GROUND = 2
OBJECT_TYPE_SKY = 3

END_ACTION_DESTROY = 0

FetchFunction = Callable[[bytes, int], np.ndarray | int | float]

COMPONENT_TYPE_BYTE = 5120
COMPONENT_TYPE_UNSIGNED_BYTE = 5121
COMPONENT_TYPE_SHORT = 5122
COMPONENT_TYPE_UNSIGNED_SHORT = 5123
COMPONENT_TYPE_UNSIGNED_INT = 5125
COMPONENT_TYPE_FLOAT = 5126

#0: debug, 1: production
GAME_MODE = 0
#endregion
#region helper functions
def get_byte_slice_from_accessor(accessor_description: dict[str, any],
    buffer_views: list[dict[str, any]], buffer_data: bytes) -> bytes:
    """
        Look at the given accessor and use it to fetch a region of buffer data
    """

    buffer_view_index = accessor_description["bufferView"]

    buffer_view = buffer_views[buffer_view_index]
    offset = buffer_view["byteOffset"]
    length = buffer_view["byteLength"]

    return buffer_data[offset:offset+length]

def get_value_list_from_accessor(accessor_description: dict[str, any],
    buffer_views: list[dict[str, any]], buffer_data: bytes) -> list[np.ndarray]:
    """
        Look at the given accessor and use it to fetch a list of arrays
        from the buffer data.
    """

    buffer_view_index = accessor_description["bufferView"]
    count = accessor_description["count"]
    _type = accessor_description["type"]
    component_type = accessor_description["componentType"]

    #get fetch function and byte stride
    fetch_function, stride = get_fetch_function(_type, component_type)

    buffer_view = buffer_views[buffer_view_index]
    offset = buffer_view["byteOffset"]

    return [fetch_function(buffer_data, offset + stride * i) for i in range(count)]

def get_fetch_function(_type: str, component_type: int) -> tuple[FetchFunction, int]:
    """ Choose an appropriate function and stride from the given data description. """

    fetch_function = get_float_3
    stride = 12
    if _type == "SCALAR":
        if component_type == COMPONENT_TYPE_BYTE:
            stride = 1
            fetch_function = get_byte_1
        elif component_type == COMPONENT_TYPE_UNSIGNED_BYTE:
            stride = 1
            fetch_function = get_unsigned_byte_1
        elif component_type == COMPONENT_TYPE_SHORT:
            stride = 2
            fetch_function = get_short_1
        elif component_type == COMPONENT_TYPE_UNSIGNED_SHORT:
            stride = 2
            fetch_function = get_unsigned_short_1
        elif component_type == COMPONENT_TYPE_UNSIGNED_INT:
            stride = 4
            fetch_function = get_unsigned_int_1
        elif component_type == COMPONENT_TYPE_FLOAT:
            stride = 4
            fetch_function = get_float_1
        else:
            print("Error! Component type not supported.")
    elif _type == "VEC2":
        if component_type == COMPONENT_TYPE_BYTE:
            stride = 2
            fetch_function = get_byte_2
        elif component_type == COMPONENT_TYPE_UNSIGNED_BYTE:
            stride = 2
            fetch_function = get_unsigned_byte_2
        elif component_type == COMPONENT_TYPE_SHORT:
            stride = 4
            fetch_function = get_short_2
        elif component_type == COMPONENT_TYPE_UNSIGNED_SHORT:
            stride = 4
            fetch_function = get_unsigned_short_2
        elif component_type == COMPONENT_TYPE_UNSIGNED_INT:
            stride = 8
            fetch_function = get_unsigned_int_2
        elif component_type == COMPONENT_TYPE_FLOAT:
            stride = 8
            fetch_function = get_float_2
        else:
            print("Error! Component type not supported.")
    elif _type == "VEC3":
        if component_type == COMPONENT_TYPE_BYTE:
            stride = 3
            fetch_function = get_byte_3
        elif component_type == COMPONENT_TYPE_UNSIGNED_BYTE:
            stride = 3
            fetch_function = get_unsigned_byte_3
        elif component_type == COMPONENT_TYPE_SHORT:
            stride = 6
            fetch_function = get_short_3
        elif component_type == COMPONENT_TYPE_UNSIGNED_SHORT:
            stride = 6
            fetch_function = get_unsigned_short_3
        elif component_type == COMPONENT_TYPE_UNSIGNED_INT:
            stride = 12
            fetch_function = get_unsigned_int_3
        elif component_type == COMPONENT_TYPE_FLOAT:
            stride = 12
            fetch_function = get_float_3
        else:
            print("Error! Component type not supported.")
    elif _type == "VEC4":
        if component_type == COMPONENT_TYPE_BYTE:
            stride = 4
            fetch_function = get_byte_4
        elif component_type == COMPONENT_TYPE_UNSIGNED_BYTE:
            stride = 4
            fetch_function = get_unsigned_byte_4
        elif component_type == COMPONENT_TYPE_SHORT:
            stride = 8
            fetch_function = get_short_4
        elif component_type == COMPONENT_TYPE_UNSIGNED_SHORT:
            stride = 8
            fetch_function = get_unsigned_short_4
        elif component_type == COMPONENT_TYPE_UNSIGNED_INT:
            stride = 16
            fetch_function = get_unsigned_int_4
        elif component_type == COMPONENT_TYPE_FLOAT:
            stride = 16
            fetch_function = get_float_4
        else:
            print("Error! Component type not supported.")
    elif _type == "MAT2":
        if component_type == COMPONENT_TYPE_BYTE:
            stride = 4
            fetch_function = get_byte_2_2
        elif component_type == COMPONENT_TYPE_UNSIGNED_BYTE:
            stride = 4
            fetch_function = get_unsigned_byte_2_2
        elif component_type == COMPONENT_TYPE_SHORT:
            stride = 8
            fetch_function = get_short_2_2
        elif component_type == COMPONENT_TYPE_UNSIGNED_SHORT:
            stride = 8
            fetch_function = get_unsigned_short_2_2
        elif component_type == COMPONENT_TYPE_UNSIGNED_INT:
            stride = 16
            fetch_function = get_unsigned_int_2_2
        elif component_type == COMPONENT_TYPE_FLOAT:
            stride = 16
            fetch_function = get_float_2_2
        else:
            print("Error! Component type not supported.")
    elif _type == "MAT3":
        if component_type == COMPONENT_TYPE_BYTE:
            stride = 9
            fetch_function = get_byte_3_3
        elif component_type == COMPONENT_TYPE_UNSIGNED_BYTE:
            stride = 9
            fetch_function = get_unsigned_byte_3_3
        elif component_type == COMPONENT_TYPE_SHORT:
            stride = 18
            fetch_function = get_short_3_3
        elif component_type == COMPONENT_TYPE_UNSIGNED_SHORT:
            stride = 18
            fetch_function = get_unsigned_short_3_3
        elif component_type == COMPONENT_TYPE_UNSIGNED_INT:
            stride = 36
            fetch_function = get_unsigned_int_3_3
        elif component_type == COMPONENT_TYPE_FLOAT:
            stride = 36
            fetch_function = get_float_3_3
        else:
            print("Error! Component type not supported.")
    elif _type == "MAT4":
        if component_type == COMPONENT_TYPE_BYTE:
            stride = 16
            fetch_function = get_byte_4_4
        elif component_type == COMPONENT_TYPE_UNSIGNED_BYTE:
            stride = 16
            fetch_function = get_unsigned_byte_4_4
        elif component_type == COMPONENT_TYPE_SHORT:
            stride = 32
            fetch_function = get_short_4_4
        elif component_type == COMPONENT_TYPE_UNSIGNED_SHORT:
            stride = 32
            fetch_function = get_unsigned_short_4_4
        elif component_type == COMPONENT_TYPE_UNSIGNED_INT:
            stride = 64
            fetch_function = get_unsigned_int_4_4
        elif component_type == COMPONENT_TYPE_FLOAT:
            stride = 64
            fetch_function = get_float_4_4
        else:
            print("Error! Component type not supported.")
    else:
        print("Error! Data type not supported.")

    return fetch_function, stride
#endregion
#region 1 element fetches
def get_byte_1(data: bytes, offset: int) -> int:

    return struct.unpack("<b", data[offset:offset + 1])[0]

def get_unsigned_byte_1(data: bytes, offset: int) -> int:

    return struct.unpack("<B", data[offset:offset + 1])[0]

def get_short_1(data: bytes, offset: int) -> int:

    return struct.unpack("<h", data[offset:offset + 2])[0]

def get_unsigned_short_1(data: bytes, offset: int) -> int:

    return struct.unpack("<H", data[offset:offset + 2])[0]

def get_unsigned_int_1(data: bytes, offset: int) -> int:

    return struct.unpack("<I", data[offset:offset + 4])[0]

def get_float_1(data: bytes, offset: int) -> float:

    return struct.unpack("<f", data[offset:offset + 4])[0]
#endregion
#region 2 element fetches
def get_byte_2(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<2b", data[offset:offset + 2]),
                    dtype=np.byte)

def get_unsigned_byte_2(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<2B", data[offset:offset + 1]),
                    dtype=np.ubyte)

def get_short_2(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<2h", data[offset:offset + 4]),
                    dtype = np.int16)

def get_unsigned_short_2(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<2H", data[offset:offset + 4]),
                    dtype = np.uint16)

def get_unsigned_int_2(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<2I", data[offset:offset + 8]),
                    dtype = np.uint32)

def get_float_2(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<2f", data[offset:offset + 8]),
                    dtype = np.float32)
#endregion
#region 3 element fetches
def get_byte_3(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<3b", data[offset:offset + 3]),
                    dtype = np.byte)

def get_unsigned_byte_3(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<3B", data[offset:offset + 3]),
                    dtype = np.ubyte)

def get_short_3(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<3h", data[offset:offset + 6]),
                    dtype = np.int16)

def get_unsigned_short_3(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<3H", data[offset:offset + 6]),
                    dtype = np.uint16)

def get_unsigned_int_3(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<3I", data[offset:offset + 12]),
                    dtype = np.uint32)

def get_float_3(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<3f", data[offset:offset + 12]),
                    dtype = np.float32)
#endregion
#region 4 element fetches
def get_byte_4(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<4b", data[offset:offset + 4]),
                    dtype = np.byte)

def get_unsigned_byte_4(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<4B", data[offset:offset + 4]),
                    dtype = np.ubyte)

def get_short_4(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<4h", data[offset:offset + 8]),
                    dtype = np.int16)

def get_unsigned_short_4(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<4H", data[offset:offset + 8]),
                    dtype = np.uint16)

def get_unsigned_int_4(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<4I", data[offset:offset + 16]),
                    dtype = np.uint32)

def get_float_4(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<4f", data[offset:offset + 16]),
                    dtype = np.float32)
#endregion
#region 2x2 element fetches
def get_byte_2_2(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<4b", data[offset:offset + 9]),
                    dtype = np.byte).reshape((2,2))

def get_unsigned_byte_2_2(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<4B", data[offset:offset + 9]),
                    dtype = np.ubyte).reshape((2,2))

def get_short_2_2(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<4h", data[offset:offset + 18]),
                    dtype = np.int16).reshape((2,2))

def get_unsigned_short_2_2(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<4H", data[offset:offset + 18]),
                    dtype = np.uint16).reshape((2,2))

def get_unsigned_int_2_2(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<4I", data[offset:offset + 36]),
                    dtype = np.uint32).reshape((2,2))

def get_float_2_2(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<4f", data[offset:offset + 36]),
                    dtype = np.float32).reshape((2,2))
#endregion
#region 3x3 element fetches
def get_byte_3_3(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<9b", data[offset:offset + 9]),
                    dtype = np.byte).reshape((3,3))

def get_unsigned_byte_3_3(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<9B", data[offset:offset + 9]),
                    dtype = np.ubyte).reshape((3,3))

def get_short_3_3(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<9h", data[offset:offset + 18]),
                    dtype = np.int16).reshape((3,3))

def get_unsigned_short_3_3(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<9H", data[offset:offset + 18]),
                    dtype = np.uint16).reshape((3,3))

def get_unsigned_int_3_3(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<9I", data[offset:offset + 36]),
                    dtype = np.uint32).reshape((3,3))

def get_float_3_3(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<9f", data[offset:offset + 36]),
                    dtype = np.float32).reshape((3,3))
#endregion
#region 4x4 element fetches
def get_byte_4_4(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<16b", data[offset:offset + 16]),
                    dtype = np.byte).reshape((4,4))

def get_unsigned_byte_4_4(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<16B", data[offset:offset + 16]),
                    dtype = np.ubyte).reshape((4,4))

def get_short_4_4(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<16h", data[offset:offset + 32]),
                    dtype = np.int16).reshape((4,4))

def get_unsigned_short_4_4(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<16H", data[offset:offset + 32]),
                    dtype = np.uint16).reshape((4,4))

def get_unsigned_int_4_4(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<16I", data[offset:offset + 64]),
                    dtype = np.uint32).reshape((4,4))

def get_float_4_4(data: bytes, offset: int) -> np.ndarray:

    return np.array(struct.unpack("<16f", data[offset:offset + 64]),
                    dtype = np.float32).reshape((4,4))
#endregion
