import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np

def create_shader(vertex_filepath: str, fragment_filepath: str) -> int:
    """
        Compile and link shader modules to make a shader program.

        Parameters:

            vertex_filepath: path to the text file storing the vertex
                            source code
            
            fragment_filepath: path to the text file storing the
                                fragment source code
        
        Returns:

            A handle to the created shader program
    """

    with open(vertex_filepath,'r') as f:
        vertex_src = f.readlines()

    with open(fragment_filepath,'r') as f:
        fragment_src = f.readlines()
    
    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                            compileShader(fragment_src, GL_FRAGMENT_SHADER))
    
    return shader

class App:
    """
        For now, the app will be handling everything.
        Later on we'll break it into subcomponents.
    """


    def __init__(self):
        """ Initialise the program """

        self._set_up_pygame()

        self._set_up_timer()

        self._set_up_opengl()
        
        self._create_assets()
    
    def _set_up_pygame(self) -> None:
        """
            Initialize and configure pygame.
        """

        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((640,480), pg.OPENGL|pg.DOUBLEBUF)

    def _set_up_timer(self) -> None:
        """
            Set up the app's timer.
        """

        self.clock = pg.time.Clock()
    
    def _set_up_opengl(self) -> None:
        """
            Configure any desired OpenGL options
        """

        glClearColor(0.1, 0.2, 0.2, 1)
    
    def _create_assets(self) -> None:
        """
            Create all of the assets needed for drawing.
        """

        self.triangle = Triangle()
        self.shader = create_shader(
            vertex_filepath = "shaders/vertex.txt", 
            fragment_filepath = "shaders/fragment.txt")
    
    def run(self) -> None:
        """ Run the app """

        running = True
        while (running):
            #check events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
            #refresh screen
            glClear(GL_COLOR_BUFFER_BIT)

            glUseProgram(self.shader)
            self.triangle.arm_for_drawing()
            self.triangle.draw()

            pg.display.flip()

            #timing
            self.clock.tick(60)

    def quit(self) -> None:
        """ cleanup the app, run exit code """

        self.triangle.destroy()
        glDeleteProgram(self.shader)
        pg.quit()

class Triangle:
    """
        Yep, it's a triangle.
    """


    def __init__(self):
        """
            Initialize a triangle.
        """
        
        # x, y, z, r, g, b
        vertices = (
            -0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
             0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
             0.0,  0.5, 0.0, 0.0, 0.0, 1.0
        )
        vertices = np.array(vertices, dtype=np.float32)

        self.vertex_count = 3

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
    
    def arm_for_drawing(self) -> None:
        """
            Arm the triangle for drawing.
        """
        glBindVertexArray(self.vao)
    
    def draw(self) -> None:
        """
            Draw the triangle.
        """

        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self) -> None:
        """
            Free any allocated memory.
        """
        
        glDeleteVertexArrays(1,(self.vao,))
        glDeleteBuffers(1,(self.vbo,))

if __name__ == "__main__":

    my_app = App()
    my_app.run()
    my_app.quit()