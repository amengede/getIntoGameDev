import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import ctypes

class Engine:
    """
        Responsible for drawing scenes
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

        #general OpenGL configuration
        glClearColor(1.0, 0.0, 0.0, 1)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.shader = self.createShader("shaders/frameBufferVertex.txt",
                                        "shaders/frameBufferFragment.txt")
        
        #define top and bottom points for a line segment
        glUseProgram(self.shader)

        self.createQuad()
        self.createColorBuffer()
    
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
    
    def createQuad(self):
        # x, y, z, s, t
        self.vertices = np.array(
            ( 1.0,  1.0, 0.0, 0.0, 1.0, #top-right
             -1.0,  1.0, 0.0, 0.0, 0.0, #top-left
             -1.0, -1.0, 0.0, 1.0, 0.0, #bottom-left
             -1.0, -1.0, 0.0, 1.0, 0.0, #bottom-left
              1.0, -1.0, 0.0, 1.0, 1.0, #bottom-right
              1.0,  1.0, 0.0, 0.0, 1.0), #top-right
             dtype=np.float32
        )

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
            [np.uint32((255<<24) + (255 << 16) + (255 << 8) + 255) for pixel in range(self.screenWidth * self.screenHeight)],
            dtype=np.uint32
        )

        self.colorBuffer = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.colorBuffer)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,self.screenHeight,self.screenWidth,0,GL_RGBA,GL_UNSIGNED_INT_8_8_8_8,bytes(self.colorBufferData))
    
    def drawScene(self):
        """
            Draw all objects in the scene
        """

        glUseProgram(self.shader)

        glClear(GL_COLOR_BUFFER_BIT)

        self.clearScreen()

        
        for x in range(self.screenWidth):
            self.drawVerticalLine(x, 20, 128, 0, 0)
        
        
        
        #self.setPixel(160, 120, 0, 0, 255)
        

        self.updateScreen()
    
    def clearScreen(self):
        self.colorBufferData &= 0
        self.colorBufferData |= ((0 << 24) + (255 << 16) + (0 << 8) + 255)
    
    def setPixel(self, x, y, r, g, b):
        """
            32 bits:
            RRRRRRRR BBBBBBBB GGGGGGGG AAAAAAAA
            00000000 00000000 00000000 RRRRRRRR: 0-255
            shift 24 bits to the left: RRRRRRRR 00000000 00000000 00000000
            00000000 00000000 00000000 BBBBBBBB: 0-255
            shift 16 bits to the left: 00000000 BBBBBBBB 00000000 00000000
        """
        self.colorBufferData[y + x * self.screenHeight] = (r<<24 + (g << 16) + (b << 8) + 255)
    
    def drawVerticalLine(self, x, height, r, g, b):
        lineHeight = min(int(height), self.screenHeight//2)
        wallTop = self.screenHeight//2 - lineHeight + x * self.screenHeight
        wallBottom = self.screenHeight//2 + lineHeight + x * self.screenHeight
        self.colorBufferData[wallTop:wallBottom] = ((r << 24) + (g << 16) + (b << 8) + 255)
    
    def updateScreen(self):
        glBindTexture(GL_TEXTURE_2D, self.colorBuffer)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,self.screenHeight,self.screenWidth,0,GL_RGBA,GL_UNSIGNED_INT_8_8_8_8,bytes(self.colorBufferData))
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        pg.display.flip()
    

class App:
    """
        Calls high level control functions (handle input, draw scene etc)
    """


    def __init__(self):
        pg.init()
        self.screenWidth = 320
        self.screenHeight = 240
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((self.screenWidth, self.screenHeight), pg.OPENGL|pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        self.graphicsEngine = Engine(self.screenWidth, self.screenHeight)
        self.mainLoop()

    def mainLoop(self):

        running = True
        while (running):
            #events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
            self.handleKeys()
            
            #render
            self.graphicsEngine.drawScene()

            #timing
            self.clock.tick()
            framerate = int(self.clock.get_fps())
            pg.display.set_caption(f"Running at {framerate} fps.")
        self.quit()
    
    def handleKeys(self):
        """
            handle the current key state
        """
        pass

    def quit(self):
        self.graphicsEngine.destroy()
        pg.quit()

myApp = App()