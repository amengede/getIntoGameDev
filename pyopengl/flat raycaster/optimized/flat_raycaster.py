import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
import math
import ctypes

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

        self.player = Player(7.5, 6.5, 90)
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
    
    def move_player(self, speed):
        """
            attempt to move the player with the given speed
        """
        dx =  speed * np.cos(np.radians(self.player.direction), dtype=np.float32)
        dy = -speed * np.sin(np.radians(self.player.direction), dtype=np.float32)
        if (int(self.player.x + dx) >= 0 and int(self.player.x + dx) < len(self.map[0])):
            if (self.map[int(self.player.y)][int(self.player.x + dx)]) == 0:
                self.player.x += dx
        if (int(self.player.y + dy) >= 0 and int(self.player.y + dy) < len(self.map)):
            if (self.map[int(self.player.y + dy)][int(self.player.x)]) == 0:
                self.player.y += dy
        #print(f"Player direction: {self.player.direction}, position: ({self.player.x}, {self.player.y})")
    
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

class Ray:
    """
        Ray used in rendering, steps along
        in a given direction from a given position.
    """

        
    def __init__(self):
            self.posX = 0.0
            self.posY = 0.0
            self.directionX = 0.0
            self.directionY = 0.0
            self.mapX = 0
            self.mapY = 0
            self.deltaDistX = 0.0
            self.deltaDistY = 0.0
            self.stepX = 0
            self.sideDistX = 0.0
            self.stepY = 0
            self.sideDistY = 0.0
            self.side = 0
        
    def orient(self,position,direction):

            (self.posX,self.posY) = position
            (self.directionX,self.directionY) = direction
            #where the ray starts
            self.mapX = math.floor(self.posX)
            self.mapY = math.floor(self.posY)

            #delta distance: distance to the next X or Y gridline
            #delta distances work once the ray is on a gridline
            if np.abs(self.directionX) < 1e-8:
                self.deltaDistX = 1e8
            else:
                self.deltaDistX = np.abs(1 / self.directionX)
            
            if np.abs(self.directionY) < 1e-8:
                self.deltaDistY = 1e8
            else:
                self.deltaDistY = np.abs(1 / self.directionY)
            self.hit = False
            if (self.directionX < 0):
                self.stepX = -1
                #some positive float less than 1
                #right - left
                self.sideDistX = (self.posX - self.mapX) * self.deltaDistX
            else:
                #right
                self.stepX = 1
                self.sideDistX = (self.mapX + 1 - self.posX) * self.deltaDistX
            
            if (self.directionY < 0):
                #ray heading up
                self.stepY = -1
                #some positive float less than 1
                #bottom - top
                self.sideDistY = (self.posY - self.mapY) * self.deltaDistY
            else:
                #down
                self.stepY = 1
                self.sideDistY = (self.mapY + 1 - self.posY) * self.deltaDistY

    def step(self):
        if (self.sideDistX < self.sideDistY):
            #step to next horizontal map square
            self.sideDistX += self.deltaDistX
            self.mapX += self.stepX
            self.side = 0 #we stepped horizontally
        else:
            self.sideDistY += self.deltaDistY
            self.mapY += self.stepY
            self.side = 1 #we stepped vertically

class RenderState:
    """
        Represents the info corresponding to a wall hit.
    """


    def __init__(self):
        self.x = 0.0
        self.scale = 0.0
        self.side = 0
        self.mapCoordinate = (0,0)
        self.complete = False

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
        glClearColor(0.1, 0.2, 0.2, 1)
        self.shader = self.createShader("shaders/flatRaycasterVertex.txt",
                                        "shaders/flatRaycasterFragment.txt")
        
        #define top and bottom points for a line segment
        glUseProgram(self.shader)
        # x, y, z
        self.vertices = np.array(
            (0.0, 0.0, 0.0,
             0.0, 0.0, 0.0,
             0.0, 0.0, 0.0,
             0.0, 0.0, 0.0,
             0.0, 0.0, 0.0,
             0.0, 0.0, 0.0), dtype=np.float32
        )

        self.vertex_count = 6

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

        self.colors = [
                        np.array([0.0,0.0,0.5],dtype=np.float32),
                        np.array([0.0,0.5,0.0],dtype=np.float32),
                        np.array([0.0,0.5,0.5],dtype=np.float32),
                        np.array([0.5,0.0,0.0],dtype=np.float32),
                        np.array([0.5,0.0,0.5],dtype=np.float32)
                    ]
        
        self.initializeViewVariables()
        self.ray = Ray()
        self.hitA = RenderState()
        self.hitB = RenderState()
        self.hitC = RenderState()
    
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
    
    def initializeViewVariables(self):
        self.forwardsX = 0.0
        self.forwardsY = 0.0
        self.rightX = 0.0
        self.rightY = 0.0
        self.interpolationCoefficient = 0.0
        self.distanceToCamera = 0.0
        self.modelTransformOriginal = pyrr.matrix44.create_identity(dtype=np.float32)
        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
        self.lastDrawnX = -1.0

    def drawScene(self, gameBoard):
        """
            Draw all objects in the scene
        """

        glUseProgram(self.shader)

        glClear(GL_COLOR_BUFFER_BIT)

        #view parameters
        self.forwardsX =  np.cos(np.radians(gameBoard.player.direction))
        self.forwardsY = -np.sin(np.radians(gameBoard.player.direction))
        self.rightX = -self.forwardsY
        self.rightY =  self.forwardsX
        self.lastDrawnX = -1.0
        self.hitA.x = -1.0
        self.hitA.complete = False
        self.hitB.complete = False

        for rayIndex in range(self.screenWidth):
            self.interpolationCoefficient = 2.0 * rayIndex / self.screenWidth - 1.0

            self.ray.orient(
                position = (gameBoard.player.x,gameBoard.player.y),
                direction = (
                    self.forwardsX + self.interpolationCoefficient * self.rightX,
                    self.forwardsY + self.interpolationCoefficient * self.rightY
                )
            )
            
            #trace ray
            self.hit = False
            while not self.hit:
                self.ray.step()
                if gameBoard.map[self.ray.mapY][self.ray.mapX] != 0:
                    self.hit = True
            #a wall was hit, calculate the distance
            #we need to get the distance to the camera plane,
            #not the player
            if self.ray.side == 0:
                self.distanceToCamera = np.abs(self.ray.sideDistX - self.ray.deltaDistX)
            else:
                self.distanceToCamera = np.abs(self.ray.sideDistY - self.ray.deltaDistY)
            if (not self.hitA.complete):
                self.hitA.complete = True
                self.populateRenderState(self.hitA)
                #premptively populate hitB for later comparison
                self.hitB.side = self.ray.side
                self.hitB.mapCoordinate = (self.ray.mapY,self.ray.mapX)
            else:
                #check the new side/coordinate against the expected one
                if self.newSegment(self.hitB, self.ray):
                    self.hitB.complete = True
                    self.hitB.x = self.interpolationCoefficient
                    self.hitC.x = self.interpolationCoefficient
                    self.populateRenderState(self.hitC)
                else:
                    self.populateRenderState(self.hitB)
                    self.hitB.x = self.interpolationCoefficient
                    self.hitC.x = self.interpolationCoefficient
            
            if self.hitA.complete and self.hitB.complete:
                self.drawSegment(self.colors[gameBoard.map[self.hitA.mapCoordinate[0]][self.hitA.mapCoordinate[1]] - 1])
        
        #may have hit the end of the line, fill everything anyway.
        
        if self.lastDrawnX < 1.0 and self.hitA.complete:
            self.populateRenderState(self.hitB)
            self.hitB.x = 1.0
            self.drawSegment(self.colors[gameBoard.map[self.hitA.mapCoordinate[0]][self.hitA.mapCoordinate[1]] - 1])
        
        self.hitA.scale = 0.0
        self.hitB.scale = 0.0
        self.hitC.scale = 0.0
        pg.display.flip()
    
    def populateRenderState(self, renderState):
        renderState.mapCoordinate = (self.ray.mapY,self.ray.mapX)
        renderState.side = self.ray.side
        renderState.scale = 1/max(self.distanceToCamera, 1e-8)
    
    def drawSegment(self, color):
        self.hitB.complete = False
        self.lastDrawnX = self.hitB.x
        self.vertices = np.array(
            (self.hitB.x,  0.5 * self.hitB.scale, 0.0,
             self.hitA.x,  0.5 * self.hitA.scale, 0.0,
             self.hitA.x, -0.5 * self.hitA.scale, 0.0,
             self.hitA.x, -0.5 * self.hitA.scale, 0.0,
             self.hitB.x, -0.5 * self.hitB.scale, 0.0,
             self.hitB.x,  0.5 * self.hitB.scale, 0.0), dtype=np.float32
        )
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        memoryHandle = glMapBuffer(GL_ARRAY_BUFFER, GL_WRITE_ONLY)
        ctypes.memmove(ctypes.c_void_p(memoryHandle), ctypes.c_void_p(self.vertices.ctypes.data), self.vertices.nbytes)
        glUnmapBuffer(GL_ARRAY_BUFFER)

        glUniform3fv(glGetUniformLocation(self.shader, "objectColor"), 1, color)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

        self.hitA.scale = self.hitC.scale
        self.hitA.mapCoordinate = (self.hitC.mapCoordinate[0],self.hitC.mapCoordinate[1])
        self.hitA.side = self.hitC.side
        self.hitA.x = self.hitB.x
        self.hitB.side = self.hitA.side
        self.hitB.mapCoordinate = (self.hitC.mapCoordinate[0],self.hitC.mapCoordinate[1])

    def newSegment(self, renderState, ray):
        if renderState.side != ray.side:
            return True
        if ray.side == 0:
            """
                ray is sliding along vertical line,
                vertical positions can differ by up to 1,
                but horizontal positions must match.
            """
            horizontalCheck = self.hitB.mapCoordinate[1] != self.ray.mapX
            verticalCheck = abs(self.hitB.mapCoordinate[0] - self.ray.mapY) > 1
        else:
            """
                ray is sliding along horizontal line,
                horizontal positions can differ by up to 1,
                but vertical positions must match.
            """
            horizontalCheck = abs(self.hitB.mapCoordinate[1] - self.ray.mapX) > 1
            verticalCheck = self.hitB.mapCoordinate[0] != self.ray.mapY
        
        return horizontalCheck or verticalCheck
    
    def destroy(self):
        """
            Free any allocated memory
        """

        glDeleteVertexArrays(1,(self.vao,))
        glDeleteBuffers(1,(self.vbo,))
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
        #self.graphicsEngine.drawScene(self.gameBoard)
        #self.quit()
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