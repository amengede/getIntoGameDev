import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr

def createShader(vertexFilepath: str, fragmentFilepath: str) -> int:
    """
        Compile and link a shader program from source.

        Parameters:

            vertexFilepath: filepath to the vertex shader source code (relative to this file)

            fragmentFilepath: filepath to the fragment shader source code (relative to this file)
        
        Returns:

            An integer, being a handle to the shader location on the graphics card
    """

    with open(vertexFilepath,'r') as f:
        vertex_src = f.readlines()

    with open(fragmentFilepath,'r') as f:
        fragment_src = f.readlines()
    
    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                            compileShader(fragment_src, GL_FRAGMENT_SHADER))
    
    return shader

class Entity:
    """ Represents a general object with a position and rotation applied"""


    def __init__(self, position: list[float], eulers: list[float]):
        """
            Initialize the entity, store its state and update its transform.

            Parameters:

                position: The position of the entity in the world (x,y,z)

                eulers: Angles (in degrees) representing rotations around the x,y,z axes.
        """

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)
    
    def make_model_transform(self) -> np.ndarray:
        """
            Calculates and returns the entity's transform matrix,
            based on its position and rotation.
        """

        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        
        model_transform = pyrr.matrix44.multiply(
            m1=model_transform, 
            m2=pyrr.matrix44.create_from_y_rotation(
                theta = np.radians(self.eulers[2]), 
                dtype=np.float32
            )
        )

        model_transform = pyrr.matrix44.multiply(
            m1=model_transform, 
            m2=pyrr.matrix44.create_from_translation(
                vec=self.position,
                dtype=np.float32
            )
        )

        return model_transform

class App:
    """ The main program """


    def __init__(self):
        """ Set up the program """

        self.set_up_pygame()

        self.make_assets()
        
        self.get_uniform_locations()

        self.mainLoop()
    
    def set_up_pygame(self) -> None:
        """ Set up the pygame environment """
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((640,480), pg.OPENGL|pg.DOUBLEBUF)
        self.clock = pg.time.Clock()

    def make_assets(self) -> None:
        """ Make any assets the program will use."""

        self.triangle_mesh = TriangleMesh()

        self.triangle = Entity(
            position = [0.5,0,0],
            eulers = [0,0,0]
        )

        self.shader = createShader("shaders/vertex.txt", "shaders/fragment.txt")

    def get_uniform_locations(self) -> None:
        """ Query and store the locations of any uniforms on the shader """

        """
            Task: fetch the location of the model uniform from our shader,
            so we can quickly upload to it later.
        """
        
        #TODO: tell OpenGL to use our shader
        #       (OpenGL can only query uniform locations if it's using that
        #       shader currently, this is a common source of frustrating
        #       errors)

        #TODO: tell OpenGL to get the uniform location,
        #       from our shader,
        #       for the "model" uniform.
        self.modelMatrixLocation = None
    
    def mainLoop(self) -> None:
        """ Runs the app """

        glClearColor(0.1, 0.2, 0.2, 1)
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
                Task: upload the model matrix to the shader.

                The matrix is 4x4 matrix, ie. 4 columns (float vectors),
                We're sending 1 matrix, and not transposing it.
            """
            #draw the triangle
            glBindVertexArray(self.triangle_mesh.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.triangle_mesh.vertex_count)

            pg.display.flip()

            #timing
            self.clock.tick(60)
        self.quit()

    def quit(self) -> None:
        """ Frees any allocated memory and quits pygame """

        self.triangle_mesh.destroy()
        glDeleteProgram(self.shader)
        pg.quit()

class TriangleMesh:
    """ A basic mesh for a triangle. """


    def __init__(self):
        """ Initialise the mesh. """

        # x, y, z, r, g, b
        self.vertices = (
            -0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
             0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
             0.0,  0.5, 0.0, 0.0, 0.0, 1.0
        )
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vertex_count = 3

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    def destroy(self) -> None:
        """ Frees any allocated memory. """
        
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))

myApp = App()