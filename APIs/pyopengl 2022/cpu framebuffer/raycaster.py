import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import math

################################## Model ######################################

class Player:
    """
        Represents the position and direction of the player
    """

    def __init__(self, x, y, direction):
        """
            Create a new player at the given position and direction.

            Parameters:
                x (float): x position
                y (float): y position
                direction (float): direction, in degrees
        """

        self.x = x
        self.y = y
        self.direction = direction

class GameBoard:
    """
        Holds pointers to all objects in the scene
    """

    def __init__(self):
        """
            Set up scene objects.
            
            TODO: read data from file
        """

        self.map = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,2,2,2,2,2,0,0,0,0,3,0,3,0,3,0,0,0,1],
            [1,0,0,0,0,0,2,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,2,0,0,0,2,0,0,0,0,3,0,0,0,3,0,0,0,1],
            [1,0,0,0,0,0,2,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,2,2,0,2,2,0,0,0,0,3,0,3,0,3,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,4,4,4,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,4,0,4,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,4,0,0,0,0,5,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,4,0,4,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,4,0,4,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,4,4,4,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        ]
        self.player = Player(7.5, 6.5, 90)

    def move_player(self, speed):
        """
        attempt to move the player with the given speed
        """
        dx =  speed * np.cos(
                        np.radians(self.player.direction),
                        dtype=np.float32
                    )
        dy = -speed * np.sin(
                        np.radians(self.player.direction),
                        dtype=np.float32
                    )
        if (int(self.player.x + dx) >= 0 \
            and int(self.player.x + dx) < len(self.map[0])):
            if self.map[int(self.player.y)][int(self.player.x + dx)] == 0:
                self.player.x += dx
        
        if (int(self.player.y + dy) >= 0 \
            and int(self.player.y + dy) < len(self.map)):
            if (self.map[int(self.player.y + dy)][int(self.player.x)]) == 0:
                self.player.y += dy
        
    def spin_player(self, angle):
        """
            shift the player's direction by the given amount, in degrees
        """
        self.player.direction += angle
        if (self.player.direction < 0):
            self.player.direction += 360
        elif (self.player.direction > 360):
            self.player.direction -= 360

################################## View #######################################

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
        self.shader = self.createShader("shaders/frameBufferVertex.txt",
                                        "shaders/frameBufferFragment.txt")
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        #define top and bottom points for a line segment
        glUseProgram(self.shader)
        
        self.createQuad()
        self.createColorBuffer()

        self.colors = [
                        (0 << 24) + (0 << 16) + (128 << 8) + 255,
                        (0 << 24) + (128 << 16) + (0 << 8) + 255,
                        (0 << 24) + (128 << 16) + (128 << 8) + 255,
                        (128 << 24) + (0 << 16) + (0 << 8) + 255,
                        (128 << 24) + (0 << 16) + (128 << 8) + 255
                    ]
    
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

    def drawScene(self, gameBoard):
        """
            Draw all objects in the scene
        """

        glUseProgram(self.shader)

        self.clearScreen()

        #view parameters
        posX = gameBoard.player.x
        posY = gameBoard.player.y
        forwardsX =  np.cos(np.radians(gameBoard.player.direction))
        forwardsY = -np.sin(np.radians(gameBoard.player.direction))
        rightX = -forwardsY
        rightY =  forwardsX

        for rayIndex in range(self.screenWidth):
            interpolationCoefficient = 2.0 * rayIndex / self.screenWidth - 1.0
            rayDirectionX = forwardsX + interpolationCoefficient * rightX
            rayDirectionY = forwardsY + interpolationCoefficient * rightY

            mapX = math.floor(posX)
            mapY = math.floor(posY)

            #delta distance: distance to the next X or Y gridline
            #delta distances work once the ray is on a gridline
            if np.abs(rayDirectionX) < 1e-8:
                deltaDistX = 1e8
            else:
                deltaDistX = np.abs(1 / rayDirectionX)
            
            if np.abs(rayDirectionY) < 1e-8:
                deltaDistY = 1e8
            else:
                deltaDistY = np.abs(1 / rayDirectionY)
            
            if (rayDirectionX < 0):
                #ray heading left
                stepX = -1
                #some positive float less than 1
                #right - left
                sideDistX = (posX - mapX) * deltaDistX
            else:
                #right
                stepX = 1
                sideDistX = (mapX + 1 - posX) * deltaDistX
            
            if (rayDirectionY < 0):
                #ray heading up
                stepY = -1
                #some positive float less than 1
                #bottom - top
                sideDistY = (posY - mapY) * deltaDistY
            else:
                #down
                stepY = 1
                sideDistY = (mapY + 1 - posY) * deltaDistY
            
            #trace ray
            hit = 0
            while (hit == 0):
                if (sideDistX < sideDistY):
                    #step to next horizontal map square
                    sideDistX += deltaDistX
                    mapX += stepX
                    side = 0 #we stepped horizontally
                else:
                    sideDistY += deltaDistY
                    mapY += stepY
                    side = 1 #we stepped vertically
                
                if gameBoard.map[mapY][mapX] != 0:
                    hit = 1
                
            if side == 0:
                distanceToCamera = np.abs(sideDistX - deltaDistX)
            else:
                distanceToCamera = np.abs(sideDistY - deltaDistY)
            
            self.drawVerticalLine(
                x = rayIndex,
                height = (self.screenHeight//2)/max(distanceToCamera,1e-8),
                color = self.colors[gameBoard.map[mapY][mapX] - 1]
            )
            
        self.updateScreen()

    def clearScreen(self):
        self.colorBufferData &= 0
        self.colorBufferData |= ((16 << 24) + (32 << 16) + (64 << 8) + 255)
    
    def drawVerticalLine(self, x, height, color):
        lineHeight = min(int(height), self.screenHeight//2)
        wallTop = self.screenHeight//2 - lineHeight + x * self.screenHeight
        wallBottom = self.screenHeight//2 + lineHeight + x * self.screenHeight
        self.colorBufferData[wallTop:wallBottom] = color
    
    def updateScreen(self):
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

################################## Control ####################################

class App:
    """
        Calls high level control functions (handle input, draw scene etc)
    """

    def __init__(self):
        pg.init()
        self.screenWidth = 640
        self.screenHeight = 480
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((self.screenWidth, self.screenHeight), pg.OPENGL|pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        self.graphicsEngine = Engine(self.screenWidth, self.screenHeight)
        self.gameBoard = GameBoard()
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
            self.graphicsEngine.drawScene(self.gameBoard)

            #timing
            self.clock.tick()
            framerate = int(self.clock.get_fps())
            pg.display.set_caption(f"Running at {framerate} fps.")
        self.quit()
    
    def handleKeys(self):
        """
            handle the current key state
        """

        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.gameBoard.move_player(0.1)
        if keys[pg.K_a]:
            self.gameBoard.spin_player(4)
        if keys[pg.K_s]:
            self.gameBoard.move_player(-0.1)
        if keys[pg.K_d]:
            self.gameBoard.spin_player(-4)
    
    def quit(self):
        self.graphicsEngine.destroy()
        pg.quit()

myApp = App()