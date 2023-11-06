from config import *

class Mesh:

    def __init__(self):

        self.vertex_count = 0

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
    
    def draw(self) -> None:
        """ Draw the mesh. """

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
    
    def destroy(self) -> None:
        """ Destroy the mesh. """

        glDeleteBuffers(1, (self.vbo,))
        glDeleteVertexArrays(1, (self.vao,))