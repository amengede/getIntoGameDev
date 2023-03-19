import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np

def createShader(vertexFilepath, fragmentFilepath):

    """
        Terminology sometimes gets confused as to what these things are,
        often these are called fragment shaders, vertex shaders, and also
        for some reason the compiled program is also called a shader.

        We're going to use this terminology out of convenience, but here's
        the truth:

        the code for the vertex and fragment stages are individually compiled
        into modules, then those modules are linked and compiled together to form
        a shader program, so we have:

        (vertex shader module) + (fragment shader module) -> (shader program)
    """

    with open(vertexFilepath,'r') as f:
        vertex_src = f.readlines()

    """
        Task 2.2: convince yourself that no sorcery is going on here,
        print vertex_src to the console, inspect its variable type etc.
    """

    with open(fragmentFilepath,'r') as f:
        fragment_src = f.readlines()
    
    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                            compileShader(fragment_src, GL_FRAGMENT_SHADER))
    
    return shader

class App:


    def __init__(self):
        """ Initialise the program """
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((640,480), pg.OPENGL|pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        glClearColor(0.1, 0.2, 0.2, 1)
        #task 2.1: make a triangle
        self.triangle: Triangle = None
        #task 2.2: create a shader using the helper function.
        self.shader = None
        #task 2.2: tell OpenGL to use the shader program
        """
            task 2.2: what actually gets stored in the self.shader variable?
            What do you think this represents?
            What will happen as you make more shaders? 
            (you could try repeatedly compiling the same code as a quick test)
            If you delete a shader and then make another, does this change anything?

            These data types are fairly opaque, but it's still fun to ask questions
            about them.
        """
        self.mainLoop()

    def mainLoop(self) -> None:
        """ Run the app """

        running = True
        while (running):
            #check events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
            #refresh screen
            glClear(GL_COLOR_BUFFER_BIT)
            
            if self.shader is not None:
                """
                    Task 2.2: Draw the triangle!
                        use the shader (It's good practice even though we only have one)
                        bind a vertex array: our triangle's vao
                        draw arrays: in triangle mode, starting at vertex 0, drawing
                            all of the triangle's vertices.
                """
                glUseProgram(self.shader)
            pg.display.flip()

            #timing
            self.clock.tick(60)
        self.quit()

    def quit(self) -> None:
        """ cleanup the app, run exit code """
        """
            Task 2.2: delete the shader program
        """
        if self.triangle is not None:
            self.triangle.destroy()
        pg.quit()

class Triangle:
    """ A simple triangle mesh """


    def __init__(self):
        """ Make a mesh """

        #x, y, z
        self.vertices = (
            -0.5, -0.5, 0.0,
             0.5, -0.5, 0.0,
             0.0,  0.5, 0.0,
        )
        """
            task 2.1: convert this tuple of floats into a numpy array

            don't forget to set dtype! Otherwise the default is np.float64,
            and that won't behave as expected.
        """

        self.vertex_count = 3

        """
            task 2.1: generate one vertex array to store the 
            vertex array object
        """
        self.vao = None
        if self.vao is not None:
            glBindVertexArray(self.vao)
        
        self.vbo = glGenBuffers(1)
        """
            task 2.1: Bind the buffer to the appropriate descriptor
            so that it'll get the data from self.vertices
        """
        #...
        upload_ready = False
        if upload_ready:
            glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        
        """
            By this point we should be done with task 2.1: sending data to the GPU
                I realize it isn't very satisfying to do this work and have no payoff,
                so the following code can query and more or less verify that we have
                done something.
        """
        print(f"Vertex Array handle: {self.vao}")
        print(f"Buffer handle: {self.vbo}")
        buffer_size = glGetBufferParameteriv(GL_ARRAY_BUFFER, GL_BUFFER_SIZE)
        print(f"Our buffer is taking up {buffer_size} bytes in memory.")

        """
            task 2.2: enable attribute 0, and create an attribute pointer to it.

            Attribute 0 is position, it has 3 elements of type float,
            the elements do not need to be normalized by the graphics pipeline
            upon consumption, the buffer has a stride of 3 floats (how many bytes is that?)
            and attribute 0 starts at the beginning (no offset)
        """
        task_2_2_ready = False
        attribute_index = None
        elements_per_attribute = None
        element_type = None
        normalized = GL_FALSE
        stride_in_bytes = None
        offset_in_bytes = None
        if task_2_2_ready:
            glEnableVertexArrayAttrib(attribute_index)
            glVertexAttribPointer(
                attribute_index, elements_per_attribute, 
                element_type, normalized,
                stride_in_bytes, ctypes.c_void_p(offset_in_bytes)
            )

    def destroy(self) -> None:
        """ Free any allocated memory """

        """
            "But wait!"
            I hear you say,
            "Python is a garbage collected language!"
            Yes it is, but we've used that garbage collected language
            to tell our GPU to store some data.

            (this is one of the challenges of PyOpenGL,
            suddenly memory leaks are possible!)
        """

        if self.vao is not None:
            glDeleteVertexArrays(1,(self.vao,))
        if self.vbo is not None:
            glDeleteBuffers(1,(self.vbo,))

if __name__ == "__main__":
    myApp = App()