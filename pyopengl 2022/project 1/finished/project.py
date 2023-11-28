import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr

class SimpleComponent:


    def __init__(self, position, velocity):

        self.position = np.array(position, dtype=np.float32)
        self.velocity = np.array(velocity, dtype=np.float32)
    
    def update(self, rate):

        self.position += rate * self.velocity

class SentientComponent:


    def __init__(self, position, eulers, health):

        self.position = np.array(position, dtype = np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)
        self.velocity = np.array([0,0,0], dtype=np.float32)
        self.state = "fallingOn"
        self.health = health
        self.canShoot = True
        self.reloadTime = 0
        self.fallTime = 0
 
    def update(self,rate):

        if self.state == "stable":
            if abs(self.velocity[1]) < 0.01:
                self.eulers[0] *= 0.9
                if abs(self.eulers[0] < 0.5):
                    self.eulers[0] = 0
            else:
                self.position += self.velocity * rate
                self.eulers[0] += 8 * self.velocity[1]

                self.position[1] = min(6,max(-6,self.position[1]))
                self.eulers[0] = min(45,max(-45,self.eulers[0]))
            
            if not self.canShoot:
                self.reloadTime -= rate
                if self.reloadTime < 0:
                    self.reloadTime = 0
                    self.canShoot = True
            
            if self.health < 0:

                self.state = "fallingOff"

        elif self.state == "fallingOn":
            self.position[2] = 0.99 + (0.9**self.fallTime) * 16
            self.fallTime += rate
            if self.position[2] < 1:
                self.fallTime = 0
                self.position[2] = 1
                self.state = "stable"
        
        else:
            self.position[2] = -8 + (0.9**self.fallTime) * 9
            self.fallTime += rate
        
class Scene:


    def __init__(self):

        self.enemySpawnRate = 0.02

        self.powerupSpawnRate = 0.02

        self.enemyShootRate = 0.02

        self.reset()

        self.xmin = 18
        self.xmax = 36
        self.ymin = -6
        self.ymax = 6

    def reset(self):

        self.player = SentientComponent(
            position = [1,0,8],
            eulers = [0, 90, 0],
            health = 18
        )

        self.enemies = []

        self.bullets = []

        self.powerups = []

    def update(self, rate):

        if np.random.uniform() < self.enemySpawnRate * rate and len(self.enemies) < 12:

            newEnemy = SentientComponent(
                position = [
                    np.random.uniform(low=self.xmin, high=self.xmax),
                    np.random.uniform(low=self.ymin, high=self.ymax),
                    8
                ],
                eulers = [0,0,0],
                health = 2
            )
            newEnemy.velocity[1] = np.random.uniform(low=-0.1,high=0.1)
            self.enemies.append(newEnemy)
        
        if np.random.uniform() < self.powerupSpawnRate * rate and len(self.powerups) < 3:

            self.powerups.append(
                SimpleComponent(
                    position = [
                        np.random.uniform(low=self.xmin, high=self.xmax),
                        np.random.uniform(low=self.ymin, high=self.ymax),
                        1
                    ],
                    velocity=[-1,0,0]
                )
            )

        self.player.update(rate)
        self.player.velocity = np.array([0, 0, 0], dtype=np.float32)
        if self.player.position[2] < -6:
            self.reset()

        hitSomething = False

        for bullet in self.bullets:
            bullet.update(rate)
            if bullet.position[0] > 48 or bullet.position[0] < 0:
                self.bullets.pop(self.bullets.index(bullet))
            
            if bullet.position[0] > self.player.position[0] - 1 \
                and bullet.position[0] < self.player.position[0] + 1 \
                and bullet.position[1] > self.player.position[1] - 1 \
                and bullet.position[1] < self.player.position[1] + 1:

                self.player.health -= 1
                hitSomething = True
            
            else:

                for enemy in self.enemies:
                    if bullet.position[0] > enemy.position[0] - 1 \
                        and bullet.position[0] < enemy.position[0] + 1 \
                        and bullet.position[1] > enemy.position[1] - 1 \
                        and bullet.position[1] < enemy.position[1] + 1:

                        enemy.health -= 1
                        hitSomething = True

                        break
            
            if hitSomething:

                self.bullets.pop(self.bullets.index(bullet))
        
        for enemy in self.enemies:
            enemy.update(rate)
            if enemy.position[1] >= self.ymax or enemy.position[1] <= self.ymin:
                enemy.velocity[1] *= -1
            
            if np.random.uniform() < self.enemyShootRate:
                self.enemy_shoot(enemy)

            if enemy.position[2] < -7:
                self.enemies.pop(self.enemies.index(enemy))

        for powerup in self.powerups:

            powerup.update(rate)

            if powerup.position[0] > self.player.position[0] - 1 \
                and powerup.position[0] < self.player.position[0] + 1 \
                and powerup.position[1] > self.player.position[1] - 1 \
                and powerup.position[1] < self.player.position[1] + 1:

                self.player.health = min(18, self.player.health + 9)
                self.powerups.pop(self.powerups.index(powerup))
    
    def move_player(self, dPos):

        self.player.velocity = dPos
    
    def player_shoot(self):

        if self.player.canShoot:
            self.bullets.append(
                SimpleComponent(
                    position = [6, self.player.position[1], 1],
                    velocity = [2, 0, 0]
                )
            )
            self.player.canShoot = False
            self.player.reloadTime = 20
    
    def enemy_shoot(self, enemy):

        if enemy.state == "stable" and enemy.canShoot:
            self.bullets.append(
                SimpleComponent(
                    position = [enemy.position[0] - 2, enemy.position[1], 1],
                    velocity = [-2, 0, 0]
                )
            )
            enemy.canShoot = False
            enemy.reloadTime = 40

class App:


    def __init__(self, screenWidth, screenHeight):

        self.screenWidth = screenWidth
        self.screenHeight = screenHeight

        self.renderer = GraphicsEngine()

        self.scene = Scene()

        self.lastTime = pg.time.get_ticks()
        self.currentTime = 0
        self.numFrames = 0
        self.frameTime = 0
        self.lightCount = 0

        self.mainLoop()

    def mainLoop(self):
        running = True
        while (running):
            #check events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        running = False
            
            self.handleKeys()

            self.scene.update(self.frameTime * 0.05)
            
            self.renderer.render(self.scene)

            #timing
            self.calculateFramerate()
        self.quit()

    def handleKeys(self):

        keys = pg.key.get_pressed()

        # left, right, space 
        if keys[pg.K_LEFT]:
            self.scene.move_player(np.array([0,0.5,0],dtype=np.float))
        elif keys[pg.K_RIGHT]:
            self.scene.move_player(np.array([0,-0.5,0],dtype=np.float))
        
        if keys[pg.K_SPACE]:
            self.scene.player_shoot()

    def calculateFramerate(self):

        self.currentTime = pg.time.get_ticks()
        delta = self.currentTime - self.lastTime
        if (delta >= 1000):
            framerate = max(1,int(1000.0 * self.numFrames/delta))
            pg.display.set_caption(f"Running at {framerate} fps.")
            self.lastTime = self.currentTime
            self.numFrames = -1
            self.frameTime = float(1000.0 / max(1,framerate))
        self.numFrames += 1

    def quit(self):
        
        self.renderer.destroy()

class GraphicsEngine:


    def __init__(self):

        self.palette = {
            "Navy": np.array([0,13/255,107/255], dtype = np.float32),
            "Purple": np.array([156/255,25/255,224/255], dtype = np.float32),
            "Pink": np.array([255/255,93/255,162/255], dtype = np.float32),
            "Orange": np.array([255/255,162/255,93/255], dtype = np.float32),
            "Teal": np.array([153/255,221/255,204/255], dtype = np.float32),
            "Red": np.array([255/255,93/255,93/255], dtype = np.float32),
            "Green": np.array([93/255,255/255,93/255], dtype = np.float32),
        }

        #initialise pygame
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((640,480), pg.OPENGL|pg.DOUBLEBUF)

        #initialise opengl
        glClearColor(self.palette["Navy"][0], self.palette["Navy"][1], self.palette["Navy"][2], 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        #create renderpasses and resources
        shader = self.createShader("shaders/vertex.txt", "shaders/fragment.txt")
        self.renderPass = RenderPass(shader)
        self.mountainMesh = Mesh("models/mountains.obj")
        self.gridMesh = Grid(48)
        self.rocketMesh = Mesh("models/rocket.obj")
        self.sphereMesh = Mesh("models/basic_sphere.obj")
        self.ufoBaseMesh = Mesh("models/ufo_base.obj")
        self.ufoTopMesh = Mesh("models/ufo_top.obj")
    
    def createShader(self, vertexFilepath, fragmentFilepath):

        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        return shader

    def render(self, scene):

        #refresh screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.renderPass.render(scene, self)

        pg.display.flip()

    def destroy(self):

        pg.quit()

class RenderPass:


    def __init__(self, shader):

        #initialise opengl
        self.shader = shader
        glUseProgram(self.shader)

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = 800/600, 
            near = 0.1, far = 100, dtype=np.float32
        )
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader,"projection"),
            1, GL_FALSE, projection_transform
        )
        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")
        self.viewMatrixLocation = glGetUniformLocation(self.shader, "view")
        self.colorLoc = glGetUniformLocation(self.shader, "object_color")

    def render(self, scene, engine):

        glUseProgram(self.shader)

        view_transform = pyrr.matrix44.create_look_at(
            eye = np.array([-10,0,4], dtype = np.float32),
            target = np.array([0,0,4], dtype = np.float32),
            up = np.array([0,0,1], dtype = np.float32), dtype = np.float32
        )
        glUniformMatrix4fv(self.viewMatrixLocation, 1, GL_FALSE, view_transform)

        #mountains
        glUniform3fv(self.colorLoc, 1, engine.palette["Teal"])
        modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
        modelTransform = pyrr.matrix44.multiply(
            m1 = modelTransform,
            m2 = pyrr.matrix44.create_from_z_rotation(theta = np.radians(90), dtype=np.float32)
        )
        modelTransform = pyrr.matrix44.multiply(
            m1 = modelTransform,
            m2 = pyrr.matrix44.create_from_translation(vec = np.array([32, 0, 0], dtype=np.float32))
        )
        glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, modelTransform)
        glBindVertexArray(engine.mountainMesh.vao)
        glDrawArrays(GL_LINES, 0, engine.mountainMesh.vertex_count)

        #ground
        glUniform3fv(self.colorLoc, 1, engine.palette["Teal"])
        modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
        modelTransform = pyrr.matrix44.multiply(
            m1 = modelTransform,
            m2 = pyrr.matrix44.create_from_translation(vec = np.array([-16, -24, 0], dtype=np.float32))
        )
        glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, modelTransform)
        glBindVertexArray(engine.gridMesh.vao)
        glDrawArrays(GL_LINES, 0, engine.gridMesh.vertex_count)

        #player
        glUniform3fv(self.colorLoc, 1, engine.palette["Orange"])
        modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
        modelTransform = pyrr.matrix44.multiply(
            m1 = modelTransform,
            m2 = pyrr.matrix44.create_from_scale(scale = np.array([0.4,0.4,0.4],dtype=np.float32))
        )
        modelTransform = pyrr.matrix44.multiply(
            m1 = modelTransform,
            m2 = pyrr.matrix44.create_from_z_rotation(theta = np.radians(-90), dtype=np.float32)
        )
        modelTransform = pyrr.matrix44.multiply(
            m1 = modelTransform,
            m2 = pyrr.matrix44.create_from_x_rotation(theta = np.radians(scene.player.eulers[0]), dtype=np.float32)
        )
        modelTransform = pyrr.matrix44.multiply(
            m1 = modelTransform,
            m2 = pyrr.matrix44.create_from_translation(vec = scene.player.position, dtype=np.float32)
        )
        glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, modelTransform)
        glBindVertexArray(engine.rocketMesh.vao)
        glDrawArrays(GL_TRIANGLES, 0, engine.rocketMesh.vertex_count)

        #bullets
        glUniform3fv(self.colorLoc, 1, engine.palette["Red"])
        for bullet in scene.bullets:
            modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
            modelTransform = pyrr.matrix44.multiply(
                m1 = modelTransform,
                m2 = pyrr.matrix44.create_from_scale(scale = np.array([0.4,0.4,0.4],dtype=np.float32))
            )
            modelTransform = pyrr.matrix44.multiply(
                m1 = modelTransform,
                m2 = pyrr.matrix44.create_from_translation(vec = bullet.position, dtype=np.float32)
            )
            glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, modelTransform)
            glBindVertexArray(engine.sphereMesh.vao)
            glDrawArrays(GL_TRIANGLES, 0, engine.sphereMesh.vertex_count)
        
        #powerups
        glUniform3fv(self.colorLoc, 1, engine.palette["Green"])
        for powerup in scene.powerups:
            modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
            modelTransform = pyrr.matrix44.multiply(
                m1 = modelTransform,
                m2 = pyrr.matrix44.create_from_scale(scale = np.array([0.4,0.4,0.4],dtype=np.float32))
            )
            modelTransform = pyrr.matrix44.multiply(
                m1 = modelTransform,
                m2 = pyrr.matrix44.create_from_translation(vec = powerup.position, dtype=np.float32)
            )
            glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, modelTransform)
            glBindVertexArray(engine.sphereMesh.vao)
            glDrawArrays(GL_TRIANGLES, 0, engine.sphereMesh.vertex_count)
        
        #enemies
        for enemy in scene.enemies:
            modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
            modelTransform = pyrr.matrix44.multiply(
                m1 = modelTransform,
                m2 = pyrr.matrix44.create_from_scale(scale = np.array([0.2,0.2,0.2],dtype=np.float32))
            )
            modelTransform = pyrr.matrix44.multiply(
                m1 = modelTransform,
                m2 = pyrr.matrix44.create_from_x_rotation(theta = np.radians(-180), dtype=np.float32)
            )
            modelTransform = pyrr.matrix44.multiply(
                m1 = modelTransform,
                m2 = pyrr.matrix44.create_from_x_rotation(theta = np.radians(enemy.eulers[0]), dtype=np.float32)
            )
            modelTransform = pyrr.matrix44.multiply(
                m1 = modelTransform,
                m2 = pyrr.matrix44.create_from_translation(vec = enemy.position, dtype=np.float32)
            )
            glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, modelTransform)
            glUniform3fv(self.colorLoc, 1, engine.palette["Purple"])
            glBindVertexArray(engine.ufoBaseMesh.vao)
            glDrawArrays(GL_TRIANGLES, 0, engine.ufoBaseMesh.vertex_count)
            glUniform3fv(self.colorLoc, 1, engine.palette["Pink"])
            glBindVertexArray(engine.ufoTopMesh.vao)
            glDrawArrays(GL_TRIANGLES, 0, engine.ufoTopMesh.vertex_count)

    def destroy(self):

        glDeleteProgram(self.shader)

class Mesh:


    def __init__(self, filename):
        # x, y, z, s, t, nx, ny, nz
        self.vertices = self.loadMesh(filename)
        self.vertex_count = len(self.vertices)//3
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
    
    def loadMesh(self, filename):

        #raw, unassembled data
        v = []
        
        #final, assembled and packed result
        vertices = []

        #open the obj file and read the data
        with open(filename,'r') as f:
            line = f.readline()
            while line:
                firstSpace = line.find(" ")
                flag = line[0:firstSpace]
                if flag=="v":
                    #vertex
                    line = line.replace("v ","")
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    v.append(l)
                elif flag=="f":
                    #face, three or more vertices in v/vt/vn form
                    line = line.replace("f ","")
                    line = line.replace("\n","")
                    #get the individual vertices for each line
                    line = line.split(" ")
                    faceVertices = []
                    for vertex in line:
                        #break out into [v,vt,vn],
                        #correct for 0 based indexing.
                        l = vertex.split("/")
                        position = int(l[0]) - 1
                        faceVertices.append(v[position])
                    # obj file uses triangle fan format for each face individually.
                    # unpack each face
                    triangles_in_face = len(line) - 2

                    vertex_order = []
                    """
                        eg. 0,1,2,3 unpacks to vertices: [0,1,2,0,2,3]
                    """
                    for i in range(triangles_in_face):
                        vertex_order.append(0)
                        vertex_order.append(i+1)
                        vertex_order.append(i+2)
                    for i in vertex_order:
                        for x in faceVertices[i]:
                            vertices.append(x)
                line = f.readline()
        return vertices
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))

class Grid:


    def __init__(self, size):

        self.vertices = []

        for i in range(size):
            self.vertices.append(i)
            self.vertices.append(0)
            self.vertices.append(0)
            self.vertices.append(i)
            self.vertices.append(size - 1)
            self.vertices.append(0)
        for j in range(size):
            self.vertices.append(0)
            self.vertices.append(j)
            self.vertices.append(0)
            self.vertices.append(size - 1)
            self.vertices.append(j)
            self.vertices.append(0)
        
        self.vertex_count = len(self.vertices)//3
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
    

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))
    
myApp = App(800,600)