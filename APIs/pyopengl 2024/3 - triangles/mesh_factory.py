from config import *


def build_triangle_mesh() -> tuple[tuple[int], int]:
    """
        Builds a mesh representing a triangle.

        Returns:

            vbos, vao. Where vbos is a tuple of the vertex buffers, and vao is the
            vertex array.
    """

    position_data = np.array(
        (-0.75, -0.75, 0.0,
        0.75, -0.75, 0.0,
        0.0, 0.75, 0.0), dtype = np.float32)
    
    color_data = np.array((0, 1,2), dtype = np.uint32)

    #generate one vertex array to hold everything.
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    #position buffer
    position_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, position_buffer)

    #attribute 0: position
    attribute_index = 0
    size = 3
    stride = 12
    offset = 0
    glVertexAttribPointer(
        attribute_index, size, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset))
    glEnableVertexAttribArray(attribute_index)

    #upload positions to GPU
    glBufferData(GL_ARRAY_BUFFER, position_data.nbytes, position_data, GL_STATIC_DRAW)

    #color buffer
    color_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, color_buffer)

    #attribute 1: color
    attribute_index = 1
    size = 1
    stride = 4
    offset = 0
    glVertexAttribIPointer(
        attribute_index, size, GL_UNSIGNED_INT, stride, ctypes.c_void_p(offset))
    glEnableVertexAttribArray(attribute_index)

    #upload colors to GPU
    glBufferData(GL_ARRAY_BUFFER, color_data.nbytes, color_data, GL_STATIC_DRAW)

    return ((position_buffer, color_buffer), vao)

def build_triangle_mesh2() -> tuple[int, int]:
    """
        Builds a mesh representing a triangle.

        Returns:

            vbo, vao.
    """

    vertex_data = np.zeros(3, dtype = data_type_vertex)
    vertex_data[0] = (-0.75, -0.75, 0.0, 0)
    vertex_data[1] = (0.75, -0.75, 0.0, 1)
    vertex_data[2] = (0.0, 0.75, 0.0, 2)

    #generate one vertex array to hold everything.
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    #vertex buffer
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)

    #attribute 0: position
    attribute_index = 0
    size = 3
    offset = 0
    glVertexAttribPointer(
        attribute_index, size, GL_FLOAT, GL_FALSE, 
        data_type_vertex.itemsize, ctypes.c_void_p(offset))
    glEnableVertexAttribArray(attribute_index)

    #attribute 1: color
    attribute_index = 1
    size = 1
    offset = 12
    glVertexAttribIPointer(
        attribute_index, size, GL_UNSIGNED_INT, 
        data_type_vertex.itemsize, ctypes.c_void_p(offset))
    glEnableVertexAttribArray(attribute_index)

    #upload vertices to GPU
    glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

    return (vbo, vao)

def build_quad_mesh() -> tuple[int, int, int]:
    """
        Builds a mesh representing a triangle.

        Returns:

            ebo, vbo, vao.
    """

    vertex_data = np.zeros(4, dtype = data_type_vertex)
    vertex_data[0] = (-0.75, -0.75, 0.0, 0)
    vertex_data[1] = (0.75, -0.75, 0.0, 1)
    vertex_data[2] = (0.75, 0.75, 0.0, 2)
    vertex_data[3] = (-0.75, 0.75, 0.0, 1)

    index_data = np.array((0, 1, 2, 2, 3, 0), dtype = np.ubyte)

    #generate one vertex array to hold everything.
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    #vertex buffer
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)

    #attribute 0: position
    attribute_index = 0
    size = 3
    offset = 0
    glVertexAttribPointer(
        attribute_index, size, GL_FLOAT, GL_FALSE, 
        data_type_vertex.itemsize, ctypes.c_void_p(offset))
    glEnableVertexAttribArray(attribute_index)

    #attribute 1: color
    attribute_index = 1
    size = 1
    offset = 12
    glVertexAttribIPointer(
        attribute_index, size, GL_UNSIGNED_INT, 
        data_type_vertex.itemsize, ctypes.c_void_p(offset))
    glEnableVertexAttribArray(attribute_index)

    #upload vertices to GPU
    glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

    #element buffer
    ebo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)

    #upload indices to GPU
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)

    return (ebo, vbo, vao)