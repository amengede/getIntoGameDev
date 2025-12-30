from config import *
import mesh

class ScreenQuad(mesh.Mesh):
    
    
    def __init__(self):

        super().__init__()

        vertices = np.array(
            ( 1.0,  1.0, #top-right
             -1.0,  1.0, #top-left
             -1.0, -1.0, #bottom-left
             -1.0, -1.0, #bottom-left
              1.0, -1.0, #bottom-right
              1.0,  1.0), #top-right
             dtype=np.float32
        )

        self.vertex_count = 6

        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))