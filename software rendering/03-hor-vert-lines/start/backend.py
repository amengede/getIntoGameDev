from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
from config import *

class EngineBackend:
    """
        Holds a colorbuffer and puts it on the screen
    """

    def __init__(self, width, height):
        """
            Initialize a flat raycasting context
            
                Parameters:
                    width (int): width of screen
                    height (int): height of screen
        """
        self.screenWidth = width
        self.screenHeight = height

        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((self.screenWidth, self.screenHeight), pg.OPENGL|pg.DOUBLEBUF)

        #general OpenGL configuration
        self.createQuad()
        self.shader = self.createShader("shaders/vertex.txt",
                                        "shaders/fragment.txt")
        
        #define top and bottom points for a line segment
        glUseProgram(self.shader)
        
        self.createColorBuffer()
    
    def get_color_buffer(self) -> np.ndarray:
        return self.colorBufferData
    
    def createQuad(self):
        # x, y, z, s, t
        self.vertices = np.array(
            ( 1.0,  1.0, 0.0, 0.0, 1.0, #top-right
             -1.0,  1.0, 0.0, 0.0, 0.0, #top-left
             -1.0, -1.0, 0.0, 1.0, 0.0, #bottom-left
             -1.0, -1.0, 0.0, 1.0, 0.0, #bottom-left
              1.0, -1.0, 0.0, 1.0, 1.0, #bottom-right
              1.0,  1.0, 0.0, 0.0, 1.0), #top-right
             dtype=np.float32)

        self.vertex_count = 6

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))
    
    def createColorBuffer(self):
        self.colorBufferData = np.array(
            [np.uint32((255<<16) + (255 << 8) + (255 << 0)) for pixel in range(self.screenWidth * self.screenHeight)],
            dtype=np.uint32
        )
        #print(self.colorBufferData.shape)

        self.colorBuffer = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.colorBuffer)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,self.screenHeight,self.screenWidth,0,GL_RGBA,GL_UNSIGNED_INT_8_8_8_8,bytes(self.colorBufferData))
    
    def createShader(self, vertexFilepath, fragmentFilepath):
        """
            Read source code, compile and link shaders.
            Returns the compiled and linked program.
        """

        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        return shader
    
    def present(self):
        glBindTexture(GL_TEXTURE_2D, self.colorBuffer)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,self.screenHeight,self.screenWidth,0,GL_RGBA,GL_UNSIGNED_INT_8_8_8_8,bytes(self.colorBufferData))
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        pg.display.flip()
    
    def destroy(self):
        """
            Free any allocated memory
        """

        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))
        glDeleteTextures(1, (self.colorBuffer,))
        glDeleteProgram(self.shader)