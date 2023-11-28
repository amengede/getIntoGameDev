import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr

############################## model ##########################################

class Player:
    def __init__(self, position, model):
        self.position = np.array(position,dtype=np.float32)
        self.moveSpeed = 1
        self.model = model
        self.direction = 0
        self.camera = None

    def move(self, direction, amount):
        self.position[0] += amount * self.moveSpeed * np.cos(np.radians(direction),dtype=np.float32)
        self.position[1] -= amount * self.moveSpeed * np.sin(np.radians(direction),dtype=np.float32)
        self.camera.position[0] += amount * self.moveSpeed * np.cos(np.radians(direction),dtype=np.float32)
        self.camera.position[1] -= amount * self.moveSpeed * np.sin(np.radians(direction),dtype=np.float32)
        self.direction = direction

    def move_towards(self, targetPosition, amount):
        directionVector = targetPosition - self.position
        angle = np.arctan2(-directionVector[1],directionVector[0])
        self.move(np.degrees(angle), amount)
    
    def draw(self):
        self.model.draw(self.position, self.direction - 90)
    
    def destroy(self):
        self.model.destroy()

class Light:
    def __init__(self, shaders, colour, position, strength, index):
        self.model = CubeBasic(shaders[0], 0.1, 0.1, 0.1, colour[0], colour[1], colour[2])
        self.colour = np.array(colour, dtype=np.float32)
        self.shader = shaders[1]
        self.position = np.array(position, dtype=np.float32)
        self.strength = strength
        self.index = index

    def update(self):
        glUseProgram(self.shader)
        glUniform3fv(glGetUniformLocation(self.shader,f"lights[{self.index}].pos"),1,self.position)
        glUniform3fv(glGetUniformLocation(self.shader,f"lights[{self.index}].color"),1,self.colour)
        glUniform1f(glGetUniformLocation(self.shader,f"lights[{self.index}].strength"),self.strength)
        glUniform1i(glGetUniformLocation(self.shader,f"lights[{self.index}].enabled"),1)

    def draw(self):
        self.model.draw(self.position)

    def destroy(self):
        self.model.destroy()

class Dot:
    def __init__(self, shader, position):
        self.model = CubeBasic(shader, 0.1, 0.1, 0.1, 1, 1, 1)
        self.shader = shader
        self.position = np.array(position, dtype=np.float32)

    def draw(self):
        self.model.draw(self.position)

    def destroy(self):
        self.model.destroy()

class Cube:
    def __init__(self, shader, material, position):
        self.material = material
        self.shader = shader
        self.position = position
        glUseProgram(shader)
        # x, y, z, s, t, nx, ny, nz
        self.vertices = (
                -0.5, -0.5, -0.5, 0, 0, 0, 0, -1,
                -0.5,  0.5, -0.5, 1, 0, 0, 0, -1,
                 0.5,  0.5, -0.5, 1, 1, 0, 0, -1,

                 0.5,  0.5, -0.5, 1, 1, 0, 0, -1,
                 0.5, -0.5, -0.5, 0, 1, 0, 0, -1,
                -0.5, -0.5, -0.5, 0, 0, 0, 0, -1,

                 0.5,  0.5,  0.5, 0, 0, 0, 0,  1,
                -0.5,  0.5,  0.5, 1, 0, 0, 0,  1,
                -0.5, -0.5,  0.5, 1, 1, 0, 0,  1,

                -0.5, -0.5,  0.5, 1, 1, 0, 0,  1,
                 0.5, -0.5,  0.5, 0, 1, 0, 0,  1,
                 0.5,  0.5,  0.5, 0, 0, 0, 0,  1,

                -0.5, -0.5,  0.5, 1, 0, -1, 0,  0,
                -0.5,  0.5,  0.5, 1, 1, -1, 0,  0,
                -0.5,  0.5, -0.5, 0, 1, -1, 0,  0,

                -0.5,  0.5, -0.5, 0, 1, -1, 0,  0,
                -0.5, -0.5, -0.5, 0, 0, -1, 0,  0,
                -0.5, -0.5,  0.5, 1, 0, -1, 0,  0,

                 0.5, -0.5, -0.5, 1, 0, 1, 0,  0,
                 0.5,  0.5, -0.5, 1, 1, 1, 0,  0,
                 0.5,  0.5,  0.5, 0, 1, 1, 0,  0,

                 0.5,  0.5,  0.5, 0, 1, 1, 0,  0,
                 0.5, -0.5,  0.5, 0, 0, 1, 0,  0,
                 0.5, -0.5, -0.5, 1, 0, 1, 0,  0,

                 0.5, -0.5,  0.5, 0, 1, 0, -1,  0,
                -0.5, -0.5,  0.5, 1, 1, 0, -1,  0,
                -0.5, -0.5, -0.5, 1, 0, 0, -1,  0,

                -0.5, -0.5, -0.5, 1, 0, 0, -1,  0,
                 0.5, -0.5, -0.5, 0, 0, 0, -1,  0,
                 0.5, -0.5,  0.5, 0, 1, 0, -1,  0,

                 0.5,  0.5, -0.5, 0, 1, 0, 1,  0,
                -0.5,  0.5, -0.5, 1, 1, 0, 1,  0,
                -0.5,  0.5,  0.5, 1, 0, 0, 1,  0,

                -0.5,  0.5,  0.5, 1, 0, 0, 1,  0,
                 0.5,  0.5,  0.5, 0, 0, 0, 1,  0,
                 0.5,  0.5, -0.5, 0, 1, 0, 1,  0
            )
        self.vertex_count = len(self.vertices)//8
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))

    def draw(self):
        glUseProgram(self.shader)
        model_transform = pyrr.matrix44.create_from_translation(vec=np.array(self.position),dtype=np.float32)
        glUniformMatrix4fv(glGetUniformLocation(self.shader,"model"),1,GL_FALSE,model_transform)
        self.material.use()
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

############################## view ###########################################

class Material:
    def __init__(self, filepath):
        self.diffuseTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.diffuseTexture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(f"{filepath}_diffuse.jpg").convert()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)
        
        self.specularTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.specularTexture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(f"{filepath}_specular.jpg").convert()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.diffuseTexture)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D,self.specularTexture)

    def destroy(self):
        glDeleteTextures(2, (self.diffuseTexture, self.specularTexture))

class ObjModel:
    def __init__(self, folderpath, filename, shader, material):
        self.shader = shader
        self.material = material
        glUseProgram(shader)
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
                        for x in theseTextures[i]:
                            self.vertices.append(x)
                        for x in theseNormals[i]:
                            self.vertices.append(x)
                    
                line = f.readline()
        self.vertices = np.array(self.vertices,dtype=np.float32)

        #vertex array object, all that stuff
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,self.vbo)
        glBufferData(GL_ARRAY_BUFFER,self.vertices.nbytes,self.vertices,GL_STATIC_DRAW)
        self.vertexCount = int(len(self.vertices)/8)

        #position attribute
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,self.vertices.itemsize*8,ctypes.c_void_p(0))
        #normal attribute
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1,2,GL_FLOAT,GL_FALSE,self.vertices.itemsize*8,ctypes.c_void_p(12))
        #texture attribute
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2,3,GL_FLOAT,GL_FALSE,self.vertices.itemsize*8,ctypes.c_void_p(20))

    def getVertices(self):
        return self.vertices

    def draw(self, position, direction):
        glUseProgram(self.shader)
        self.material.use()
        model_transform = pyrr.matrix44.create_identity()
        angle = np.radians(direction)
        model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_z_rotation(theta=angle, dtype=np.float32))
        model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_translation(position, dtype=np.float32))
        glUniformMatrix4fv(glGetUniformLocation(self.shader,"model"),1,GL_FALSE,model_transform)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES,0,self.vertexCount)
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class CubeBasic:
    def __init__(self, shader, l, w, h, r, g, b):
        self.shader = shader
        glUseProgram(shader)
        # x, y, z, r, g, b
        self.vertices = (
                -l/2, -w/2, -h/2, r, g, b,
                -l/2,  w/2, -h/2, r, g, b,
                 l/2,  w/2, -h/2, r, g, b,

                 l/2,  w/2, -h/2, r, g, b,
                 l/2, -w/2, -h/2, r, g, b,
                -l/2, -w/2, -h/2, r, g, b,

                 l/2,  w/2,  h/2, r, g, b,
                -l/2,  w/2,  h/2, r, g, b,
                -l/2, -w/2,  h/2, r, g, b,

                -l/2, -w/2,  h/2, r, g, b,
                 l/2, -w/2,  h/2, r, g, b,
                 l/2,  w/2,  h/2, r, g, b,

                -l/2, -w/2,  h/2, r, g, b,
                -l/2,  w/2,  h/2, r, g, b,
                -l/2,  w/2, -h/2, r, g, b,

                -l/2,  w/2, -h/2, r, g, b,
                -l/2, -w/2, -h/2, r, g, b,
                -l/2, -w/2,  h/2, r, g, b,

                 l/2, -w/2, -h/2, r, g, b,
                 l/2,  w/2, -h/2, r, g, b,
                 l/2,  w/2,  h/2, r, g, b,

                 l/2,  w/2,  h/2, r, g, b,
                 l/2, -w/2,  h/2, r, g, b,
                 l/2, -w/2, -h/2, r, g, b,

                 l/2, -w/2,  h/2, r, g, b,
                -l/2, -w/2,  h/2, r, g, b,
                -l/2, -w/2, -h/2, r, g, b,

                -l/2, -w/2, -h/2, r, g, b,
                 l/2, -w/2, -h/2, r, g, b,
                 l/2, -w/2,  h/2, r, g, b,

                 l/2,  w/2, -h/2, r, g, b,
                -l/2,  w/2, -h/2, r, g, b,
                -l/2,  w/2,  h/2, r, g, b,

                -l/2,  w/2,  h/2, r, g, b,
                 l/2,  w/2,  h/2, r, g, b,
                 l/2,  w/2, -h/2, r, g, b
            )
        self.vertex_count = len(self.vertices)//6
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    def draw(self, position):
        glUseProgram(self.shader)
        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_translation(vec=position,dtype=np.float32))
        glUniformMatrix4fv(glGetUniformLocation(self.shader,"model"),1,GL_FALSE,model_transform)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class Camera:
    def __init__(self, position, targetObject):
        self.position = np.array(position,dtype=np.float32)
        self.forward = np.array([0, 0, 0],dtype=np.float32)
        self.right = np.array([0, 0, 0],dtype=np.float32)
        self.up = np.array([0, 0, 0],dtype=np.float32)
        self.global_up = np.array([0, 0, 1], dtype=np.float32)
        self.targetObject = targetObject

    def update(self, shaders, frameTime):
        self.forward = pyrr.vector.normalize(self.targetObject.position - self.position)
        self.right = pyrr.vector.normalize(pyrr.vector3.cross(self.forward, self.global_up))
        self.up = pyrr.vector.normalize(pyrr.vector3.cross(self.right, self.forward))

        lookat_matrix = pyrr.matrix44.create_look_at(self.position, self.targetObject.position, self.up,dtype=np.float32)
        for shader in shaders:
            glUseProgram(shader)
            glUniformMatrix4fv(glGetUniformLocation(shader,"view"),1,GL_FALSE,lookat_matrix)
            glUniform3fv(glGetUniformLocation(shader,"cameraPos"),1,self.position)


############################## control ########################################

class App:
    def __init__(self):
        #initialise pygame
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((640,480), pg.OPENGL|pg.DOUBLEBUF)
        pg.mouse.set_visible(False)
        pg.mouse.set_pos((320,240))
        self.lastTime = 0
        self.currentTime = 0
        self.numFrames = 0
        self.frameTime = 0
        self.lightCount = 0
        #initialise opengl
        glClearColor(0.1, 0.1, 0.1, 1)
        self.shader = self.createShader("shaders/vertex.txt", "shaders/fragment.txt")
        self.shaderBasic = self.createShader("shaders/simple_3d_vertex.txt", "shaders/simple_3d_fragment.txt")
        glUseProgram(self.shader)
        self.resetLights()
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        projection_transform = pyrr.matrix44.create_perspective_projection(45, 640/480, 0.1, 10, dtype=np.float32)
        glUniformMatrix4fv(glGetUniformLocation(self.shader,"projection"),1,GL_FALSE,projection_transform)

        glUniform3fv(glGetUniformLocation(self.shader,"ambient"), 1, np.array([0.1, 0.1, 0.1],dtype=np.float32))

        glUniform1i(glGetUniformLocation(self.shader, "material.diffuse"), 0)
        glUniform1i(glGetUniformLocation(self.shader, "material.specular"), 1)

        glUseProgram(self.shaderBasic)

        glUniformMatrix4fv(glGetUniformLocation(self.shaderBasic,"projection"),1,GL_FALSE,projection_transform)
        
        glEnable(GL_DEPTH_TEST)

        self.wood_texture = Material("gfx/crate")
        monkey_model = ObjModel("models", "monkey.obj", self.shader, self.wood_texture)
        self.player = Player([0,1,0], monkey_model)
        self.camera = Camera([-3,1,3], self.player)
        self.player.camera = self.camera
        self.light = Light([self.shaderBasic, self.shader], [0.2, 0.7, 0.8], [1,1.7,1.5], 2, self.lightCount)
        self.lightCount += 1
        self.light2 = Light([self.shaderBasic, self.shader], [0.9, 0.4, 0.0], [0,1.7,0.5], 2, self.lightCount)
        self.lightCount += 1
        self.click_dots = []
        #make cubes
        self.cubes = []
        self.cubes.append(Cube(self.shader, self.wood_texture,[1,1,0.5]))
        self.cubes.append(Cube(self.shader, self.wood_texture,[4,1,0.5]))
        self.cubes.append(Cube(self.shader, self.wood_texture,[7,1,0.5]))
        self.cubes.append(Cube(self.shader, self.wood_texture,[10,1,0.5]))
        self.cubes.append(Cube(self.shader, self.wood_texture,[13,1,0.5]))
        self.cubes.append(Cube(self.shader, self.wood_texture,[16,1,0.5]))
        self.mainLoop()

    def createShader(self, vertexFilepath, fragmentFilepath):

        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        return shader

    def resetLights(self):
        glUseProgram(self.shader)
        for i in range(8):
            glUniform1i(glGetUniformLocation(self.shader,f"lights[{i}].enabled"),0)

    def mainLoop(self):
        running = True
        while (running):
            #check events
            for event in pg.event.get():
                if (event.type == pg.KEYDOWN and event.key==pg.K_ESCAPE):
                    running = False
            self.handleMouse()
            self.handleKeys()
            #update objects
            self.light.update()
            self.light2.update()
            self.camera.update([self.shaderBasic, self.shader], self.frameTime)
            
            #refresh screen
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.light.draw()
            self.light2.draw()
            for cube in self.cubes:
                cube.draw()
            self.player.draw()
            for dot in self.click_dots:
                dot.draw()
            pg.display.flip()

            #timing
            self.showFrameRate()
        self.quit()

    def handleKeys(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            forward = self.camera.forward
            self.player.move_towards(self.player.position + forward, 0.0025 * self.frameTime)
        if keys[pg.K_a]:
            right = -self.camera.right
            self.player.move_towards(self.player.position + right, 0.0025 * self.frameTime)
        if keys[pg.K_s]:
            forward = -self.camera.forward
            self.player.move_towards(self.player.position + forward, 0.0025 * self.frameTime)
        if keys[pg.K_d]:
            right = self.camera.right
            self.player.move_towards(self.player.position + right, 0.0025 * self.frameTime)

    def handleMouse(self):
        up = self.camera.up
        right = self.camera.right
        (x,y) = pg.mouse.get_pos()
        rightAmount = (x - 320)/640
        upAmount = (240 - y)/480
        self.camera.position -= 0.1 * self.frameTime * rightAmount * right
        self.camera.position -= 0.1 * self.frameTime * upAmount * up
        pg.mouse.set_pos((320,240))

    def showFrameRate(self):
        self.currentTime = pg.time.get_ticks()
        delta = self.currentTime - self.lastTime
        if (delta >= 1000):
            framerate = int(1000.0 * self.numFrames/delta)
            pg.display.set_caption(f"Running at {framerate} fps.")
            self.lastTime = self.currentTime
            self.numFrames = -1
            self.frameTime = float(1000.0 / max(framerate,60))
        self.numFrames += 1

    def quit(self):
        self.wood_texture.destroy()
        self.player.destroy()
        self.light.destroy()
        self.light2.destroy()
        for cube in self.cubes:
                cube.destroy()
        for dot in self.click_dots:
                dot.destroy()
        glDeleteProgram(self.shader)
        pg.quit()

###############################################################################

myApp = App()