from config import *

class StaticGeometry:


    def __init__(self):

        # x, y, z
        self.vertices: np.ndarray = np.array([], dtype=np.float32)
    
    def consume(self, vertices: np.ndarray, model_transform: np.ndarray):
        
        #"reshape" into [x, y, z, 1]
        vertex_count = int(len(vertices) // 3)
        raw_vertices = np.ones(vertex_count * 4, dtype=np.float32)
        
        for i in range(vertex_count):
            raw_vertices[4*i:4*i + 3] = vertices[3*i:3*(i + 1)]
        
        raw_vertices = np.reshape(raw_vertices, (vertex_count,4))

        #transform by matrix
        raw_vertices = pyrr.matrix44.multiply(raw_vertices, model_transform)

        #pack into array
        for i in range(vertex_count):
            self.vertices = np.append(self.vertices, raw_vertices[i][0:3])
    
    def finalize(self):

        self.vertex_count = int(len(self.vertices) // 3)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

    def destroy(self):

        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

static_geometry_model = StaticGeometry()