import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr

################################## Model ######################################

class Player:
    """
        Represents the position and direction of the player
    """

    def __init__(self, x):
        """
            Create a new player at the given position and direction.

            Parameters:
                x (float): x position
                y (float): y position
                direction (float): direction, in degrees
        """

        self.x = x
        self.y = 2
        self.state = "falling"
        self.fall_t = 0
        self.rollVelocity = 0
        self.rollAmount = 0
        self.shootT = 0
        self.reloadTime = 16
        self.canShoot = True
        self.shot = False
    
    def update(self):

        if self.state == "falling":
            self.y = -0.2 + (0.9**self.fall_t) * 2
            self.fall_t += 1
            if self.y < -0.2:
                self.y = -0.2
                self.state = "stable"
        
        if self.shot:
            self.canShoot = False
            self.shot = False
            self.shootT = self.reloadTime
        
        if not self.canShoot:
            self.shootT -= 1
            if self.shootT < 0:
                self.shootT = 0
                self.canShoot = True
        
        elif self.state == "stable":
            if abs(self.rollVelocity) > 0:
                self.rollAmount /= 1.1
                if abs(self.rollAmount) < 0.1:
                    self.rollAmount = 0
                    self.rollVelocity = 0
        
        elif self.state == "moving":
            self.rollAmount = min(45, max(-45, self.rollAmount + self.rollVelocity))

    def move(self, dx):

        nextX = self.x + dx
        if nextX > -0.5 and nextX < 0.5:
            self.x = nextX
            self.rollVelocity = dx * 90
            self.state = "moving"

    def stabilize(self):
        if self.state == "moving":
            self.state = "stable"

class UFO:
    

    def __init__(self, x):
        

        self.x = x
        self.y = 2
        self.state = "falling"
        self.fall_t = 0
        self.shootT = 0
        self.reloadTime = 16
        self.canShoot = True
        self.shot = False
        self.velocity = 0.01
    
    def update(self):

        if self.state == "falling":
            self.y = -0.2 + (0.9**self.fall_t) * 2
            self.fall_t += 1
            if self.y < -0.2:
                self.y = -0.2
                self.state = "stable"
        
        if self.shot:
            self.canShoot = False
            self.shot = False
            self.shootT = self.reloadTime
        
        if not self.canShoot:
            self.shootT -= 1
            if self.shootT < 0:
                self.shootT = 0
                self.canShoot = True
        
        self.x += self.velocity
        if self.x < -0.5:
            self.velocity = 0.01
        if self.x > 0.5:
            self.velocity = -0.01

class Bullet:
    """
        Represents the position and direction of the player
    """

    def __init__(self, x, z, velocity):
        """
            Create a new player at the given position and direction.

            Parameters:
                x (float): x position
                y (float): y position
                direction (float): direction, in degrees
        """

        self.x = x
        self.y = -0.2
        self.z = z
        self.velocity = velocity
        self.t = 0
    
    def update(self):
        self.t += 1
        self.z += self.velocity

class Camera:

    
    def getPosition(self, theta):

        return np.array(
            [
                0,
                12 + 3 * np.sin(np.radians(theta/2)),
                2
            ],
            dtype=np.float32
        )
    
    def getForwards(self, theta):

        return np.array(
            [
                1,
                0.2 * np.sin(np.radians(2 * theta)),
                0
            ],
            dtype=np.float32
        )
    
    def getUp(self, theta):

        return np.array(
            [
                np.cos(np.radians(theta/2)),
                np.sin(np.radians(theta/2)),
                2
            ],
            dtype=np.float32
        )
    
class GameBoard:
    """
        Holds pointers to all objects in the scene
    """

    def __init__(self):
        """
            Set up scene objects.
        """

        self.player = Player(0)
        self.bullets = []
        self.UFOs = []
        self.UFOs.append(UFO(0))
        self.camera = Camera()

    def update(self):

        for bullet in self.bullets:
            bullet.update()
            if bullet.t > 16:
                self.bullets.pop(self.bullets.index(bullet))
        
        for ufo in self.UFOs:
            ufo.update()
            if ufo.canShoot:
                if np.random.uniform() > 0.9:
                    ufo.shot = True
                    self.bullets.append(Bullet(ufo.x, -2, 0.1))

        
        self.player.update()
    
    def move_player(self, speed):
        """
        attempt to move the player with the given speed
        """
        if abs(speed) < 0.01:
            self.player.stabilize()
        else:
            self.player.move(speed)

    def playerShoot(self):
        if self.player.canShoot:
            self.player.shot = True
            self.bullets.append(Bullet(self.player.x, -0.75, -0.2))

################################## View #######################################

def groundZ(i,j,size):

    return 0

def mountainZ(i,j, size):

    if i > (size - 1)/2:
        i = size - 1 - i
    
    if j > (size - 1)/2:
        j = size - 1 - j
    
    z_i = i + i * 0.5 * np.random.uniform()

    z_j = j + j * 0.5 * np.random.uniform()

    return np.sqrt(z_i * z_j)

class ObjModel:


    def __init__(self, folderpath, filename, color):
        v = []
        vt = []
        vn = []
        self.vertices = []

        #open the obj file and read the data
        with open(f"{folderpath}/{filename}",'r') as f:
            line = f.readline()
            while line:
                firstSpace = line.find(" ")
                flag = line[0:firstSpace]
                if flag=="mtllib":
                    #declaration of material file
                    pass
                elif flag=="v":
                    #vertex
                    line = line.replace("v ","")
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    v.append(l)
                    #print(v)
                elif flag=="vt":
                    #texture coordinate
                    line = line.replace("vt ","")
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    vt.append(l)
                elif flag=="vn":
                    #normal
                    line = line.replace("vn ","")
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    vn.append(l)
                elif flag=="f":
                    #face, four vertices in v/vt/vn form
                    line = line.replace("f ","")
                    line = line.replace("\n","")
                    line = line.split(" ")
                    theseVertices = []
                    theseTextures = []
                    theseNormals = []
                    for vertex in line:
                        l = vertex.split("/")
                        position = int(l[0]) - 1
                        theseVertices.append(v[position])
                        texture = int(l[1]) - 1
                        theseTextures.append(vt[texture])
                        normal = int(l[2]) - 1
                        theseNormals.append(vn[normal])
                    # obj file uses triangle fan format for each face individually.
                    # unpack each face
                    triangles_in_face = len(line) - 2

                    vertex_order = []
                    for i in range(triangles_in_face):
                        vertex_order.append(0)
                        vertex_order.append(i+1)
                        vertex_order.append(i+2)
                    for i in vertex_order:
                        for x in theseVertices[i]:
                            self.vertices.append(x)
                        """
                        for x in theseTextures[i]:
                            self.vertices.append(x)
                        for x in theseNormals[i]:
                            self.vertices.append(x)
                        """
                        self.vertices.append(color[0])
                        self.vertices.append(color[1])
                        self.vertices.append(color[2])
                    
                line = f.readline()
        self.vertices = np.array(self.vertices,dtype=np.float32)

        #vertex array object, all that stuff
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,self.vbo)
        glBufferData(GL_ARRAY_BUFFER,self.vertices.nbytes,self.vertices,GL_STATIC_DRAW)
        self.vertex_count = int(len(self.vertices)/6)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class GroundGrid:


    def __init__(self, size, color):

        self.vertices = []
        for i in range(size):
            self.vertices.append(i)
            self.vertices.append(0)
            self.vertices.append(0)
            self.vertices.append(color[0])
            self.vertices.append(color[1])
            self.vertices.append(color[2])
            self.vertices.append(i)
            self.vertices.append(size-1)
            self.vertices.append(0)
            self.vertices.append(color[0])
            self.vertices.append(color[1])
            self.vertices.append(color[2])
        for j in range(size):
            self.vertices.append(0)
            self.vertices.append(j)
            self.vertices.append(0)
            self.vertices.append(color[0])
            self.vertices.append(color[1])
            self.vertices.append(color[2])
            self.vertices.append(size-1)
            self.vertices.append(j)
            self.vertices.append(0)
            self.vertices.append(color[0])
            self.vertices.append(color[1])
            self.vertices.append(color[2])
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.vertex_count = int(self.vertices.size / 6)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class Engine:
    """
        Responsible for drawing scenes
    """

    def __init__(self, width, height):
        """
            Initialize the graphics engine
            
                Parameters:
                    width (int): width of screen
                    height (int): height of screen
        """
        
        self.palette = {
            "dark-violet": (48/255,3/255,80/255),
            "purple": (148/255,22/255,127/255),
            "pink": (233/255,52/255,121/255),
            "orange": (249/255, 172/255, 83/255),
            "light-pink": (246/255, 46/255, 141/255),
            "blue": (21/255, 60/255, 180/255)
        }
        self.screenWidth = width
        self.screenHeight = height
        self.theta = 0

        #general OpenGL configuration
        glClearColor(self.palette["blue"][0], self.palette["blue"][1], self.palette["blue"][2], 1)

        self.ground = GroundGrid(24, self.palette["light-pink"])
        self.playerModel = ObjModel("models", "rocket.obj", self.palette["orange"])
        self.ufoBase = ObjModel("models", "ufo_base.obj", self.palette["dark-violet"])
        self.ufoTop = ObjModel("models", "ufo_top.obj", self.palette["orange"])
        self.bullet = ObjModel("models", "basic_sphere.obj", self.palette["orange"])
        self.powerUp = ObjModel("models", "basic_sphere.obj", self.palette["blue"])

        #top
        start_corner = (0,0)
        sizes = (2,4,8,16)
        self.vertices = np.array([],dtype=np.float32)
        while start_corner[0] < 24:
            size = sizes[np.random.randint(low = 0, high=4)]
            while start_corner[0] + size - 1 > 24:
                size = sizes[np.random.randint(low = 0, high=4)]
            self.vertices = np.concatenate((self.vertices,self.makeGrid(
                        origin = (start_corner[0], -size + 1),
                        size = size,
                        z = mountainZ,
                        color = self.palette["purple"]
                    )))
            start_corner = (start_corner[0] + size - 1, 0)
        
        #right
        start_corner = (24,0)
        while start_corner[1] < 24:
            size = sizes[np.random.randint(low = 0, high=4)]
            while start_corner[1] + size - 1 > 24:
                size = sizes[np.random.randint(low = 0, high=4)]
            self.vertices = np.concatenate(
                (
                    self.vertices,
                    self.makeGrid(
                        origin = (23, start_corner[1]),
                        size = size,
                        z = mountainZ,
                        color = self.palette["purple"]
                    )
            )
            )
            start_corner = (23, start_corner[1] + size - 1)
        
        #bottom
        start_corner = (0,23)
        while start_corner[0] < 24:
            size = sizes[np.random.randint(low = 0, high=4)]
            while start_corner[0] + size - 1 > 24:
                size = sizes[np.random.randint(low = 0, high=4)]
            self.vertices = np.concatenate(
                (
                    self.vertices,
                    self.makeGrid(
                        origin = (start_corner[0], 23),
                        size = size,
                        z = mountainZ,
                        color = self.palette["purple"]
                    )
            )
            )
            start_corner = (start_corner[0] + size - 1, 23)
        
        #left
        start_corner = (0,0)
        while start_corner[1] < 24:
            size = sizes[np.random.randint(low = 0, high=4)]
            while start_corner[1] + size - 1 > 24:
                size = sizes[np.random.randint(low = 0, high=4)]
            self.vertices = np.concatenate(
                (
                    self.vertices,
                    self.makeGrid(
                        origin = (-size + 1, start_corner[1]),
                        size = size,
                        z = mountainZ,
                        color = self.palette["purple"]
                    )
            )
            )
            start_corner = (0, start_corner[1] + size - 1)

        self.vertex_count = int(self.vertices.size / 6)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, 
                        self.vertices, GL_STATIC_DRAW)
        
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

        self.shader = self.createShader("shaders/vertex.txt",
                                        "shaders/fragment.txt")
        
        glUseProgram(self.shader)
        glEnable(GL_DEPTH_TEST)
        #glLineWidth(2.0)
        self.modelLocation = glGetUniformLocation(self.shader, "model")
        self.viewProjLocation = glGetUniformLocation(self.shader, "viewProjection")
    
    def update(self):

        self.theta += 1.6
        if self.theta > 360:
            self.theta -= 360
    
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

    def makeGrid(self, origin, size, z, color):

        grid = []

        height = [[z(i,j,size) for j in range(size)] for i in range(size)]

        #interior
        for i in range(size - 1):
            for j in range(size - 1):

                grid.append(origin[0] + i)
                grid.append(origin[1] + j)
                grid.append(height[i][j])
                grid.append(color[0])
                grid.append(color[1])
                grid.append(color[2])

                grid.append(origin[0] + i)
                grid.append(origin[1] + j + 1)
                grid.append(height[i][j + 1])
                grid.append(color[0])
                grid.append(color[1])
                grid.append(color[2])

                grid.append(origin[0] + i)
                grid.append(origin[1] + j)
                grid.append(height[i][j])
                grid.append(color[0])
                grid.append(color[1])
                grid.append(color[2])

                grid.append(origin[0] + i + 1)
                grid.append(origin[1] + j)
                grid.append(height[i + 1][j])
                grid.append(color[0])
                grid.append(color[1])
                grid.append(color[2])
        
        #right
        for i in range(size - 1):

            grid.append(origin[0] + i)
            grid.append(origin[1] + size - 1)
            grid.append(height[i][size - 1])
            grid.append(color[0])
            grid.append(color[1])
            grid.append(color[2])

            grid.append(origin[0] + i + 1)
            grid.append(origin[1] + size - 1)
            grid.append(height[i + 1][size - 1])
            grid.append(color[0])
            grid.append(color[1])
            grid.append(color[2])
        
        #bottom
        for j in range(size - 1):

            grid.append(origin[0] + size - 1)
            grid.append(origin[1] + j)
            grid.append(height[size - 1][j])
            grid.append(color[0])
            grid.append(color[1])
            grid.append(color[2])

            grid.append(origin[0] + size - 1)
            grid.append(origin[1] + j + 1)
            grid.append(height[size - 1][j+1])
            grid.append(color[0])
            grid.append(color[1])
            grid.append(color[2])
        
        return np.array(grid, dtype=np.float32)

    def drawScene(self, gameBoard):
        """
            Draw all objects in the scene
        """

        glUseProgram(self.shader)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        viewProjectionMatrix = pyrr.matrix44.create_identity(dtype=np.float32)
        viewProjectionMatrix = pyrr.matrix44.multiply(
            m1 = viewProjectionMatrix, 
            m2 = pyrr.matrix44.create_look_at(
                eye = gameBoard.camera.getPosition(self.theta),
                target = gameBoard.camera.getPosition(self.theta) + gameBoard.camera.getForwards(self.theta),
                up = gameBoard.camera.getUp(self.theta),
                dtype=np.float32
            )
        )
        viewProjectionMatrix = pyrr.matrix44.multiply(
            m1 = viewProjectionMatrix, 
            m2 = pyrr.matrix44.create_perspective_projection(
                fovy = 90, aspect = self.screenWidth/self.screenHeight, 
                near = 0.1, far = 64, 
                dtype=np.float32
            )
        )

        modelMatrix = pyrr.matrix44.create_identity(dtype=np.float32)

        glUniformMatrix4fv(self.modelLocation, 1, False, modelMatrix)

        glUniformMatrix4fv(self.viewProjLocation, 1, False, viewProjectionMatrix)

        glBindVertexArray(self.vao)

        glDrawArrays(GL_LINES, 0, self.vertex_count)

        modelMatrix = pyrr.matrix44.create_from_translation(np.array([-self.theta/180, 0, 0], dtype=np.float32),dtype=np.float32)

        glUniformMatrix4fv(self.modelLocation, 1, False, modelMatrix)

        glBindVertexArray(self.ground.vao)

        glDrawArrays(GL_LINES, 0, self.ground.vertex_count)

        viewProjectionMatrix = pyrr.matrix44.create_identity(dtype=np.float32)
        viewProjectionMatrix = pyrr.matrix44.multiply(
            m1 = viewProjectionMatrix, 
            m2 = pyrr.matrix44.create_perspective_projection(
                fovy = 90, aspect = self.screenWidth/self.screenHeight, 
                near = 0.1, far = 64, 
                dtype=np.float32
            )
        )

        modelMatrix = pyrr.matrix44.create_identity(dtype=np.float32)
        modelMatrix = pyrr.matrix44.multiply(modelMatrix,pyrr.matrix44.create_from_scale(scale = np.array([0.02, 0.02, 0.02]),dtype=np.float32))
        modelMatrix = pyrr.matrix44.multiply(modelMatrix,pyrr.matrix44.create_from_x_rotation(theta=np.radians(270),dtype=np.float32))
        modelMatrix = pyrr.matrix44.multiply(modelMatrix,pyrr.matrix44.create_from_z_rotation(theta=np.radians(gameBoard.player.rollAmount),dtype=np.float32))
        modelMatrix = pyrr.matrix44.multiply(modelMatrix,pyrr.matrix44.create_from_translation(vec = np.array([gameBoard.player.x, gameBoard.player.y, -0.4]),dtype=np.float32))
        glUniformMatrix4fv(self.modelLocation, 1, False, modelMatrix)
        glUniformMatrix4fv(self.viewProjLocation, 1, False, viewProjectionMatrix)
        glBindVertexArray(self.playerModel.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.playerModel.vertex_count)

        for bullet in gameBoard.bullets:
            modelMatrix = pyrr.matrix44.create_identity(dtype=np.float32)
            modelMatrix = pyrr.matrix44.multiply(modelMatrix,pyrr.matrix44.create_from_scale(scale = np.array([0.02, 0.02, 0.02]),dtype=np.float32))
            modelMatrix = pyrr.matrix44.multiply(modelMatrix,pyrr.matrix44.create_from_translation(vec = np.array([bullet.x, bullet.y, bullet.z]),dtype=np.float32))
            glUniformMatrix4fv(self.modelLocation, 1, False, modelMatrix)
            glBindVertexArray(self.bullet.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.bullet.vertex_count)
        
        for ufo in gameBoard.UFOs:
            modelMatrix = pyrr.matrix44.create_identity(dtype=np.float32)
            modelMatrix = pyrr.matrix44.multiply(modelMatrix,pyrr.matrix44.create_from_scale(scale = np.array([0.02, 0.02, 0.02]),dtype=np.float32))
            modelMatrix = pyrr.matrix44.multiply(modelMatrix,pyrr.matrix44.create_from_x_rotation(theta=np.radians(270),dtype=np.float32))
            modelMatrix = pyrr.matrix44.multiply(modelMatrix,pyrr.matrix44.create_from_translation(vec = np.array([ufo.x, -0.1, -2]),dtype=np.float32))
            glUniformMatrix4fv(self.modelLocation, 1, False, modelMatrix)
            glBindVertexArray(self.ufoBase.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.ufoBase.vertex_count)
            glBindVertexArray(self.ufoTop.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.ufoTop.vertex_count)


        pg.display.flip()

    def destroy(self):
        """
            Free any allocated memory
        """

        self.ground.destroy()

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
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        self.screenWidth = 800
        self.screenHeight = 600
        pg.display.set_mode((self.screenWidth, self.screenHeight), pg.OPENGL|pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        self.graphicsEngine = Engine(self.screenWidth, self.screenHeight)
        self.gameBoard = GameBoard()
        self.clock = pg.time.Clock()
        self.mainLoop()
    
    def mainLoop(self):

        running = True
        while (running):
            #events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
            self.handleKeys()

            self.gameBoard.update()
            self.graphicsEngine.update()
            
            #render
            self.graphicsEngine.drawScene(self.gameBoard)

            #timing
            self.clock.tick()
            framerate = int(self.clock.get_fps())
            pg.display.set_caption(f"Running at {framerate} fps.")
            self.clock.tick(60)
        self.quit()
    
    def handleKeys(self):
        """
            handle the current key state
        """

        keys = pg.key.get_pressed()

        if keys[pg.K_a]:
            self.gameBoard.move_player(-0.025)
        elif keys[pg.K_d]:
            self.gameBoard.move_player(0.025)
        else:
            self.gameBoard.move_player(0)
        
        if keys[pg.K_SPACE]:
            self.gameBoard.playerShoot()
    
    def quit(self):
        self.graphicsEngine.destroy()
        pg.quit()

myApp = App()