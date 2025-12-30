import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr

################################## Model ######################################

class Camera:
    """
        Represents a camera in the scene
    """

    def __init__(self, position, direction):
        """
            Create a new camera at the given position facing in the given direction.

            Parameters:
                position (numpy array [3,1])
                direction (numpy array [3,1])
        """

        self.position = position
        self.direction = direction
        self.right = np.cross(self.direction, np.array([0, 1, 0], dtype=np.float32))
        self.up = np.cross(self.right, self.direction)

class Sphere:
    """
        Represents a sphere in the scene
    """

    def __init__(self, center, radius, color):
        """
            Create a new sphere

            Parameters:
                center (numpy array [3,1])
                radius (float)
                color (numpy array [3,1])
        """

        self.center = center
        self.radius = radius
        self.color = color

class DirectionalLight:
    """
        A directional light
    """


    def __init__(self, direction, color):
        """
            Parameters:
                direction (numpy array [3,1])
                color (numpy array [3,1])
        """
        self.direction = direction
        self.color = color

class Scene:
    """
        Holds pointers to all objects in the scene
    """


    def __init__(self):
        """
            Set up scene objects.
            
            TODO: read data from file
        """

        self.spheres = [
            Sphere(
                center = np.array([0, 0, -1], dtype=np.float32),
                radius = 0.5,
                color = np.array([45/255, 128/255, 60/255], dtype=np.float32)
            ),
        ]

        self.sun = DirectionalLight(
            direction = np.array([-1,-1,-1], dtype=np.float32),
            color = np.array([1,1,1], dtype=np.float32)
        )

        self.camera = Camera(
            position = np.array([0, 0, 0], dtype=np.float32),
            direction = np.array([0, 0, -1], dtype=np.float32)
        )

################################## View #######################################

class Ray:
    """
        Abstract ray for rendering, has a start position and a direction
    """


    def __init__(self, position, direction):
        """
            Parameters:
                position (numpy array [3,1])
                direction (numpy array [3,1])
        """

        self.position = position
        self.direction = direction
    
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
    
    def createQuad(self):
        # x, y, z, s, t
        self.vertices = np.array(
            ( 1.0,  1.0, 0.0, 1.0, 1.0, #top-right
             -1.0,  1.0, 0.0, 0.0, 1.0, #top-left
             -1.0, -1.0, 0.0, 0.0, 0.0, #bottom-left
             -1.0, -1.0, 0.0, 0.0, 0.0, #bottom-left
              1.0, -1.0, 0.0, 1.0, 0.0, #bottom-right
              1.0,  1.0, 0.0, 1.0, 1.0), #top-right
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

        self.colorBuffer = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.colorBuffer)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,self.screenWidth,self.screenHeight,0,GL_RGBA,GL_UNSIGNED_INT_8_8_8_8,bytes(self.colorBufferData))
    
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

    def setPixel(self, x, y, color):
        self.colorBufferData[x + y * self.screenWidth] = (color[0] << 24) + (color[1] << 16) + (color[2] << 8) + 255
    
    def hitSphere(self, ray, sphere):
        co = ray.position - sphere.center
        a = np.dot(ray.direction, ray.direction)
        b = 2 * np.dot(co, ray.direction)
        c = np.dot(co, co) - sphere.radius * sphere.radius
        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return -1
        return (-b - np.sqrt(discriminant)) / (2 * a)
    
    def renderScene(self, scene):
        """
            Draw all objects in the scene
        """

        glUseProgram(self.shader)

        for y in range(self.screenHeight):
            for x in range(self.screenWidth):
                limitingFactor = max(self.screenWidth/2, self.screenHeight/2)
                horizontalCoefficient = (x - self.screenWidth / 2) / limitingFactor
                verticalCoefficient = (y - self.screenHeight / 2) / limitingFactor
                ray = Ray(
                    position = scene.camera.position,
                    direction = scene.camera.direction \
                        + horizontalCoefficient * scene.camera.right \
                            + verticalCoefficient * scene.camera.up
                )
                rayColor = (128, 192, 192)
                for sphere in scene.spheres:
                    tHit = self.hitSphere(ray, sphere)
                    if tHit > 0:
                        sphereNormal = pyrr.vector.normalize(ray.position + tHit * ray.direction - sphere.center)
                        lightingAmount = max(0, np.dot(sphereNormal, -scene.sun.direction))
                        rayColor = (
                            int(255 * sphere.color[0] * scene.sun.color[0] * lightingAmount),
                            int(255 * sphere.color[1] * scene.sun.color[1] * lightingAmount),
                            int(255 * sphere.color[2] * scene.sun.color[2] * lightingAmount)
                        )
                        break
                self.setPixel(x,y,rayColor)


    def clearScreen(self):
        self.colorBufferData &= 0
        self.colorBufferData |= ((16 << 24) + (32 << 16) + (64 << 8) + 255)
    
    def drawScreen(self):
        glBindTexture(GL_TEXTURE_2D, self.colorBuffer)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,self.screenWidth,self.screenHeight,0,GL_RGBA,GL_UNSIGNED_INT_8_8_8_8,bytes(self.colorBufferData))
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
        self.scene = Scene()
        self.graphicsEngine.renderScene(self.scene)
        self.mainLoop()
    
    def mainLoop(self):

        running = True
        while (running):
            #events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
            
            #render
            self.graphicsEngine.drawScreen()

            #timing
            self.clock.tick()
            framerate = int(self.clock.get_fps())
            pg.display.set_caption(f"Running at {framerate} fps.")
        self.quit()
    
    def quit(self):
        self.graphicsEngine.destroy()
        pg.quit()

myApp = App()