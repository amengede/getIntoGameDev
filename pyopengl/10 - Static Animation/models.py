import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
import ctypes

############################# Model ###########################################

class Player:
    def __init__(self, position):
        self.position = np.array(position,dtype=np.float32)
        self.forward = np.array([0, 0, 0],dtype=np.float32)
        self.theta = 0
        self.phi = 0
        self.moveSpeed = 1
        self.global_up = np.array([0, 0, 1], dtype=np.float32)

    def move(self, direction, amount):
        walkDirection = (direction + self.theta) % 360
        self.position[0] += amount * self.moveSpeed * np.cos(np.radians(walkDirection),dtype=np.float32)
        self.position[1] += amount * self.moveSpeed * np.sin(np.radians(walkDirection),dtype=np.float32)

    def increment_direction(self, theta_increase, phi_increase):
        self.theta = (self.theta + theta_increase) % 360
        self.phi = min(max(self.phi + phi_increase,-89),89)

    def update(self,shaders):
        camera_cos = np.cos(np.radians(self.theta),dtype=np.float32)
        camera_sin = np.sin(np.radians(self.theta),dtype=np.float32)
        camera_cos2 = np.cos(np.radians(self.phi),dtype=np.float32)
        camera_sin2 = np.sin(np.radians(self.phi),dtype=np.float32)
        self.forward[0] = camera_cos * camera_cos2
        self.forward[1] = camera_sin * camera_cos2
        self.forward[2] = camera_sin2
        
        right = pyrr.vector3.cross(self.global_up,self.forward)
        up = pyrr.vector3.cross(self.forward,right)
        lookat_matrix = pyrr.matrix44.create_look_at(self.position, self.position + self.forward, up,dtype=np.float32)
        for shader in shaders:
            glUseProgram(shader)
            glUniformMatrix4fv(glGetUniformLocation(shader,"view"),1,GL_FALSE,lookat_matrix)
            glUniform3fv(glGetUniformLocation(shader,"cameraPos"),1,self.position)

class Monkey:
    def __init__(self, position, model):
        self.model = model
        self.position = position

    def draw(self):
        self.model.draw(self.position)

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

class Spring:
    def __init__(self, position, animatedModel):
        self.model = animatedModel
        self.position = position

    def update(self, frametime):
        self.model.update(frametime)

    def draw(self):
        self.model.draw(self.position)

    def destroy(self):
        self.model.destroy()

############################# View ############################################

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

class CubeBasic:
    def __init__(self, shader, l, w, h, r, g, b):
        self.shader = shader
        glUseProgram(shader)
        # x, y, z, r, g, b
        self.vertices = (
                -l/2, -w/2, -h/2, r, g, b,
                 l/2, -w/2, -h/2, r, g, b,
                 l/2,  w/2, -h/2, r, g, b,

                 l/2,  w/2, -h/2, r, g, b,
                -l/2,  w/2, -h/2, r, g, b,
                -l/2, -w/2, -h/2, r, g, b,

                -l/2, -w/2,  h/2, r, g, b,
                 l/2, -w/2,  h/2, r, g, b,
                 l/2,  w/2,  h/2, r, g, b,

                 l/2,  w/2,  h/2, r, g, b,
                -l/2,  w/2,  h/2, r, g, b,
                -l/2, -w/2,  h/2, r, g, b,

                -l/2,  w/2,  h/2, r, g, b,
                -l/2,  w/2, -h/2, r, g, b,
                -l/2, -w/2, -h/2, r, g, b,

                -l/2, -w/2, -h/2, r, g, b,
                -l/2, -w/2,  h/2, r, g, b,
                -l/2,  w/2,  h/2, r, g, b,

                 l/2,  w/2,  h/2, r, g, b,
                 l/2,  w/2, -h/2, r, g, b,
                 l/2, -w/2, -h/2, r, g, b,

                 l/2, -w/2, -h/2, r, g, b,
                 l/2, -w/2,  h/2, r, g, b,
                 l/2,  w/2,  h/2, r, g, b,

                -l/2, -w/2, -h/2, r, g, b,
                 l/2, -w/2, -h/2, r, g, b,
                 l/2, -w/2,  h/2, r, g, b,

                 l/2, -w/2,  h/2, r, g, b,
                -l/2, -w/2,  h/2, r, g, b,
                -l/2, -w/2, -h/2, r, g, b,

                -l/2,  w/2, -h/2, r, g, b,
                 l/2,  w/2, -h/2, r, g, b,
                 l/2,  w/2,  h/2, r, g, b,

                 l/2,  w/2,  h/2, r, g, b,
                -l/2,  w/2,  h/2, r, g, b,
                -l/2,  w/2, -h/2, r, g, b
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

class ObjModel:
    def __init__(self,folderpath,filename, shader, material):
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

    def draw(self, position):
        glUseProgram(self.shader)
        self.material.use()
        model_transform = pyrr.matrix44.create_from_translation(position, dtype=np.float32)
        glUniformMatrix4fv(glGetUniformLocation(self.shader,"model"),1,GL_FALSE,model_transform)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES,0,self.vertexCount)
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class AnimatedModel:
    def __init__(self, shader, frames, models, material):
        self.frames = frames
        self.models = models
        self.shader = shader
        glUseProgram(shader)
        self.frame = 0
        self.vertices = models[0].getVertices()
        self.maxFrame = frames[len(frames) - 1]
        self.material = material

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

    def update(self, frametime):
        self.frame += frametime / 1000.0
        if (self.frame > self.maxFrame):
            self.frame -= self.maxFrame

    def draw(self, position):
        glUseProgram(self.shader)

        #find next and previous frames
        previousFrame = self.frames[len(self.frames) - 1]
        previousModel = self.models[len(self.frames) - 1]
        nextFrame = self.frames[0]
        nextModel = self.models[0]
        for i in range(len(self.frames)):
            if self.frames[i] > self.frame:
                previousFrame = self.frames[i - 1]
                previousModel = self.models[i - 1]
                nextFrame = self.frames[i]
                nextModel = self.models[i]
                break
        
        #interpolate between frames
        interpolationAmount = (self.frame - previousFrame) / (nextFrame - previousFrame)
        self.vertices = (1 - interpolationAmount) * previousModel.getVertices() + interpolationAmount * nextModel.getVertices()

        #load new vertex data to shader
        glBindBuffer(GL_ARRAY_BUFFER,self.vbo)
        memoryHandle = glMapBuffer(GL_ARRAY_BUFFER, GL_WRITE_ONLY)
        ctypes.memmove(ctypes.c_void_p(memoryHandle), ctypes.c_void_p(self.vertices.ctypes.data), self.vertices.nbytes)
        glUnmapBuffer(GL_ARRAY_BUFFER)
        self.material.use()
        model_transform = pyrr.matrix44.create_from_translation(position, dtype=np.float32)
        glUniformMatrix4fv(glGetUniformLocation(self.shader,"model"),1,GL_FALSE,model_transform)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES,0,self.vertexCount)

    def destroy(self):
        for model in self.models:
            model.destroy()

############################# Control #########################################

class App:
    def __init__(self):
        #initialise pygame
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((640,480), pg.OPENGL|pg.DOUBLEBUF)
        pg.mouse.set_pos((320,240))
        pg.mouse.set_visible(False)
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

        projection_transform = pyrr.matrix44.create_perspective_projection(45, 640/480, 0.1, 10, dtype=np.float32)
        glUniformMatrix4fv(glGetUniformLocation(self.shader,"projection"),1,GL_FALSE,projection_transform)

        glUniform3fv(glGetUniformLocation(self.shader,"ambient"), 1, np.array([0.1, 0.1, 0.1],dtype=np.float32))

        glUniform1i(glGetUniformLocation(self.shader, "material.diffuse"), 0)
        glUniform1i(glGetUniformLocation(self.shader, "material.specular"), 1)

        glUseProgram(self.shaderBasic)

        glUniformMatrix4fv(glGetUniformLocation(self.shaderBasic,"projection"),1,GL_FALSE,projection_transform)
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        #materials
        self.wood_texture = Material("gfx/crate")
        #models
        self.monkey_model = ObjModel("models", "monkey.obj", self.shader, self.wood_texture)
        frame1 = ObjModel("models/cube", "cube1.obj", self.shader, self.wood_texture)
        frame2 = ObjModel("models/cube", "cube2.obj", self.shader, self.wood_texture)
        self.springy_box = AnimatedModel(self.shader, [0, 60, 120], [frame1, frame2, frame1], self.wood_texture)
        #objects
        self.spring = Spring(np.array([2,2,0],dtype=np.float32), self.springy_box)
        self.monkey = Monkey(np.array([0,0,0],dtype=np.float32), self.monkey_model)
        self.player = Player([0,0,1.2])
        self.light = Light([self.shaderBasic, self.shader], [0.2, 0.7, 0.8], [1,1.7,1.5], 2, self.lightCount)
        self.lightCount += 1
        self.light2 = Light([self.shaderBasic, self.shader], [0.9, 0.4, 0.0], [0,1.7,0.5], 2, self.lightCount)
        self.lightCount += 1
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
            self.spring.update(40*self.frameTime)
            self.light.update()
            self.light2.update()
            self.player.update([self.shaderBasic, self.shader])
            #refresh screen
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.spring.draw()
            self.light.draw()
            self.light2.draw()
            self.monkey.draw()
            pg.display.flip()

            #timing
            self.showFrameRate()
        self.quit()

    def handleKeys(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.player.move(0, 0.0025*self.frameTime)
            return
        if keys[pg.K_a]:
            self.player.move(90, 0.0025*self.frameTime)
            return
        if keys[pg.K_s]:
            self.player.move(180, 0.0025*self.frameTime)
            return
        if keys[pg.K_d]:
            self.player.move(-90, 0.0025*self.frameTime)
            return

    def handleMouse(self):
        (x,y) = pg.mouse.get_pos()
        theta_increment = self.frameTime * 0.05 * (320 - x)
        phi_increment = self.frameTime * 0.05 * (240 - y)
        self.player.increment_direction(theta_increment, phi_increment)
        pg.mouse.set_pos((320,240))

    def showFrameRate(self):
        self.currentTime = pg.time.get_ticks()
        delta = self.currentTime - self.lastTime
        if (delta >= 1000):
            framerate = int(1000.0 * self.numFrames/delta)
            pg.display.set_caption(f"Running at {framerate} fps.")
            self.lastTime = self.currentTime
            self.numFrames = -1
            self.frameTime = float(1000.0 / framerate)
        self.numFrames += 1

    def quit(self):
        self.wood_texture.destroy()
        self.spring.destroy()
        self.monkey.destroy()
        self.light.destroy()
        self.light2.destroy()
        glDeleteProgram(self.shader)
        pg.quit()

###############################################################################

myApp = App()