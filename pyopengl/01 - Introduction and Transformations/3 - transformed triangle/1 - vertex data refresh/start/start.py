import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr

def createShader(vertexFilepath, fragmentFilepath):

    with open(vertexFilepath,'r') as f:
        vertex_src = f.readlines()

    with open(fragmentFilepath,'r') as f:
        fragment_src = f.readlines()
    
    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                            compileShader(fragment_src, GL_FRAGMENT_SHADER))
    
    return shader

class Entity:
    """ Basic description of anything which has a position and rotation"""


    def __init__(self, position, eulers):

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)

class App:


    def __init__(self):
        """ Create the program """

        #initialise pygame
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((640,480), pg.OPENGL|pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        #initialise opengl
        glClearColor(0.1, 0.2, 0.2, 1)

        self.triangle_mesh = TriangleMesh()

        self.shader = createShader("shaders/vertex.txt", "shaders/fragment.txt")
        glUseProgram(self.shader)

        self.triangle = Entity(
            position = [0.5,0,0],
            eulers = [0,0,0]
        )

        self.mainLoop()

    def mainLoop(self) -> None:

        running = True
        while (running):
            #check events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
            
            #update triangle
            self.triangle.eulers[2] += 0.25
            if self.triangle.eulers[2] > 360:
                self.triangle.eulers[2] -= 360
            
            #refresh screen
            glClear(GL_COLOR_BUFFER_BIT)
            glUseProgram(self.shader)

            """
                Task: Transform the triangle mesh!
            """

            #TODO: make a model transform matrix, set it to the identity
            model_transform = None
            
            #TODO: multiply a y axis rotation onto the model transform,
            #       Which angle should be used?
            #       Does pyrr expect degrees or radians?
            
            #TODO: multiply a translation onto the model transform
            
            self.triangle_mesh.build_vertices(model_transform)
            glBindVertexArray(self.triangle_mesh.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.triangle_mesh.vertex_count)

            pg.display.flip()

            #timing
            self.clock.tick(60)
        self.quit()

    def quit(self) -> None:
        self.triangle_mesh.destroy()
        glDeleteProgram(self.shader)
        pg.quit()

class TriangleMesh:


    def __init__(self):

        self.originalPositions = (
            pyrr.vector4.create(-0.5, -0.5, 0.0, 1.0, dtype=np.float32),
            pyrr.vector4.create( 0.5, -0.5, 0.0, 1.0, dtype=np.float32),
            pyrr.vector4.create( 0.0,  0.5, 0.0, 1.0, dtype=np.float32)
        )
        self.originalColors = (
            pyrr.vector3.create(1.0, 0.0, 0.0, dtype=np.float32),
            pyrr.vector3.create(0.0, 1.0, 0.0, dtype=np.float32),
            pyrr.vector3.create(0.0, 0.0, 1.0, dtype=np.float32)
        )
        
        self.vertex_count = 3

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        self.build_vertices(pyrr.matrix44.create_identity(dtype=np.float32))

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        
    def build_vertices(self, transform: np.ndarray) -> None:
        """
            Builds the mesh's vertices by applying the given transform
            to its original data, then uploads the transformed mesh
            data to its buffer.
        """

        if transform is None:
            return

        self.vertices = np.array([],dtype=np.float32)

        for i in range(self.vertex_count):

            pass

            #TODO: multiply the i-th original position by the transform
            #       store it in a new variable so the original data is
            #       untouched.
            
            #TODO: append the x,y,z components of the transformed position
            #       to self.vertices.
            #       
            #   Hint: use numpy append and take a slice

            #TODO: append the i-th original color to self.vertices

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

    def destroy(self):
        
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))

if __name__ == "__main__":

    """
        Task: before we get to the actual graphics, let's practice
        some linear algebra and transforms!
    """

    #TODO: create a pyrr vector4, set it to (1,1,1,1)
    # Print it to the console and verify that it looks reasonable

    #TODO: create a pyrr matrix44 translation, translate by (1, 2, 3)
    # Print it to the console and verify it
    
    #TODO: multiply the point by the translation transform,
    # Print the result to the console and verify it

    #TODO: create a pyrr matrix44 scale, use scale factors (1, 2, 3)
    # Print it to the console and verify it
    
    #TODO: multiply the point by the scale transform,
    # Print the result to the console and verify it

    myApp = App()