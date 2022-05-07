import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
import random

##################################### Model ###################################

class FixedComponent:


    def __init__(self, position, eulers):

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)

class Light:


    def __init__(self, position, color):

        self.position = np.array(position, dtype=np.float32)
        self.color = np.array(color, dtype=np.float32)

class Player:


    def __init__(self, position, eulers):
        self.position = np.array(position,dtype=np.float32)
        self.eulers = np.array(eulers,dtype=np.float32)
        self.moveSpeed = 1
        self.global_up = np.array([0, 0, 1], dtype=np.float32)

    def move(self, direction, amount):
        walkDirection = (direction + self.eulers[1]) % 360
        self.position[0] += amount * self.moveSpeed * np.cos(np.radians(walkDirection),dtype=np.float32)
        self.position[1] += amount * self.moveSpeed * np.sin(np.radians(walkDirection),dtype=np.float32)

    def increment_direction(self, theta_increase, phi_increase):
        self.eulers[1] = (self.eulers[1] + theta_increase) % 360
        self.eulers[0] = min(max(self.eulers[0] + phi_increase,-89),89)

    def get_forwards(self):

        return np.array(
            [
                #x = cos(theta) * cos(phi)
                np.cos(
                    np.radians(
                        self.eulers[1]
                    ),dtype=np.float32
                ) * np.cos(
                    np.radians(
                        self.eulers[0]
                    ),dtype=np.float32
                ),

                #y = sin(theta) * cos(phi)
                np.sin(
                    np.radians(
                        self.eulers[1]
                    ),dtype=np.float32
                ) * np.cos(
                    np.radians(
                        self.eulers[0]
                    ),dtype=np.float32
                ),

                #x = sin(phi)
                np.sin(
                    np.radians(
                        self.eulers[0]
                    ),dtype=np.float32
                )
            ], dtype = np.float32
        )
    
    def get_up(self):

        forwards = self.get_forwards()
        right = np.cross(
            a = forwards,
            b = self.global_up
        )

        return np.cross(
            a = right,
            b = forwards,
        )

class Scene:


    def __init__(self):

        self.containers = [
            FixedComponent(
                position = [0,0,0],
                eulers = [0,0,0]
            ),
        ]

        self.monkeys = [
            FixedComponent(
                position = [5,0,0],
                eulers = [0,0,0]
            ),
            FixedComponent(
                position = [9,0,0],
                eulers = [0,0,0]
            ),
            FixedComponent(
                position = [9,9,0],
                eulers = [0,0,0]
            ),
        ]

        self.lights = [
            Light(
                position = [-9, -9, 19],
                color = [random.uniform(a = 0.5, b = 1) for x in range(3)]
            ),
            Light(
                position = [9, -9, 19],
                color = [random.uniform(a = 0.5, b = 1) for x in range(3)]
            ),
            Light(
                position = [-9, 9, 19],
                color = [random.uniform(a = 0.5, b = 1) for x in range(3)]
            ),
            Light(
                position = [9, 9, 19],
                color = [random.uniform(a = 0.5, b = 1) for x in range(3)]
            ),
            Light(
                position = [-9, -9, 1],
                color = [random.uniform(a = 0.5, b = 1) for x in range(3)]
            ),
            Light(
                position = [9, -9, 1],
                color = [random.uniform(a = 0.5, b = 1) for x in range(3)]
            ),
            Light(
                position = [-9, 9, 1],
                color = [random.uniform(a = 0.5, b = 1) for x in range(3)]
            ),
            Light(
                position = [9, 9, 1],
                color = [random.uniform(a = 0.5, b = 1) for x in range(3)]
            )
        ]

        self.player = Player(
            position = [0, 0, 2],
            eulers = [0, 0, 0]
        )
    
    def update(self):

        pass

##################################### Control #################################

class App:


    def __init__(self):

        self.lastTime = 0
        self.currentTime = 0
        self.numFrames = 0
        self.frameTime = 0
        self.lightCount = 0
        #initialise pygame
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((640,480), pg.OPENGL|pg.DOUBLEBUF)
        pg.mouse.set_pos((320,240))
        pg.mouse.set_visible(False)

        self.scene = Scene()

        self.engine = Engine(self.scene)

        self.mainLoop()

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
            self.scene.update()
            #refresh screen
            self.engine.draw(self.scene)
            self.showFrameRate()
        self.quit()

    def handleKeys(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.scene.player.move(0, 0.0025*self.frameTime)
            return
        if keys[pg.K_a]:
            self.scene.player.move(90, 0.0025*self.frameTime)
            return
        if keys[pg.K_s]:
            self.scene.player.move(180, 0.0025*self.frameTime)
            return
        if keys[pg.K_d]:
            self.scene.player.move(-90, 0.0025*self.frameTime)
            return

    def handleMouse(self):
        (x,y) = pg.mouse.get_pos()
        theta_increment = self.frameTime * 0.05 * (320 - x)
        phi_increment = self.frameTime * 0.05 * (240 - y)
        self.scene.player.increment_direction(theta_increment, phi_increment)
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

        self.engine.quit()
        pg.quit()

##################################### View ####################################

class Engine:


    def __init__(self, scene):

        #initialise opengl
        glClearColor(0.1, 0.1, 0.1, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        self.shaderGPass = self.createShader(
            "shaders/g_vertex.txt",
            "shaders/g_fragment.txt"
        )

        self.shaderLPass = self.createShader(
            "shaders/l_vertex.txt", 
            "shaders/l_fragment.txt"
        )
        self.shaderColored = self.createShader(
            "shaders/simple_3d_vertex.txt", 
            "shaders/simple_3d_fragment.txt"
        )

        self.get_uniform_locations()

        self.set_initial_uniform_values()

        self.create_assets(scene)

        self.create_framebuffer()

    def createShader(self, vertexFilepath, fragmentFilepath):

        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()

        temp1 = compileShader(vertex_src, GL_VERTEX_SHADER)
        temp2 = compileShader(fragment_src, GL_FRAGMENT_SHADER)
        
        shader = compileProgram(temp1,
                                temp2)
        
        return shader

    def get_uniform_locations(self):

        glUseProgram(self.shaderGPass)
        self.viewLocgPass = glGetUniformLocation(self.shaderGPass, "view")

        glUseProgram(self.shaderLPass)
        self.lightLocTextured = {

            "pos": [
                glGetUniformLocation(
                    self.shaderLPass,f"lights[{i}].position"
                ) 
                for i in range(8)
            ],

            "color": [
                glGetUniformLocation(
                    self.shaderLPass,f"lights[{i}].color"
                ) 
                for i in range(8)
            ],

            "strength": [
                glGetUniformLocation(
                    self.shaderLPass,f"lights[{i}].strength"
                ) 
                for i in range(8)
            ],

            "count": glGetUniformLocation(
                self.shaderLPass,f"lightCount"
            )
        }

        self.cameraLocTextured = glGetUniformLocation(self.shaderLPass, "viewPos")

        glUseProgram(self.shaderColored)
        self.viewLocUntextured = glGetUniformLocation(self.shaderColored, "view")
        self.modelLocUntextured = glGetUniformLocation(self.shaderColored, "model")
        self.colorLocUntextured = glGetUniformLocation(self.shaderColored, "color")

    def set_initial_uniform_values(self):

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = 640/480, 
            near = 0.1, far = 40, dtype=np.float32
        )

        glUseProgram(self.shaderGPass)
        glUniformMatrix4fv(
            glGetUniformLocation(
                self.shaderGPass,"projection"
            ),
            1,GL_FALSE,projection_transform
        )

        glUniform1i(
            glGetUniformLocation(
                self.shaderGPass, "material.albedo"
            ), 0
        )

        glUniform1i(
            glGetUniformLocation(
                self.shaderGPass, "material.ao"
            ), 1
        )

        glUniform1i(
            glGetUniformLocation(
                self.shaderGPass, "material.normal"
            ), 2
        )

        glUniform1i(
            glGetUniformLocation(
                self.shaderGPass, "material.specular"
            ), 3
        )

        glUseProgram(self.shaderLPass)
        glUniform3fv(
            glGetUniformLocation(
                self.shaderLPass,"ambient"
            ), 
            1, np.array([0.1, 0.1, 0.1],dtype=np.float32)
        )

        glUniform1i(
            glGetUniformLocation(
                self.shaderLPass, "fragmentData.position"
            ), 0
        )

        glUniform1i(
            glGetUniformLocation(
                self.shaderLPass, "fragmentData.albedoSpecular"
            ), 1
        )

        glUniform1i(
            glGetUniformLocation(
                self.shaderLPass, "fragmentData.normalAo"
            ), 2
        )

        glUseProgram(self.shaderColored)
        glUniformMatrix4fv(
            glGetUniformLocation(
                self.shaderColored,"projection"
            ),1,GL_FALSE,projection_transform
        )
    
    def create_assets(self,scene):

        glUseProgram(self.shaderGPass)
        self.wood_texture = Material("crate", "png")

        self.container_mesh = ObjMesh("models/container.obj")
        self.containerTransforms = np.array([
            pyrr.matrix44.create_identity(dtype = np.float32)
            for i in range(len(scene.containers))
        ], dtype=np.float32)
        glBindVertexArray(self.container_mesh.vao)
        self.containerTransformVBO = glGenBuffers(1)
        glBindBuffer(
            GL_ARRAY_BUFFER, 
            self.containerTransformVBO
        )
        glBufferData(
            GL_ARRAY_BUFFER, 
            self.containerTransforms.nbytes, 
            self.containerTransforms, 
            GL_STATIC_DRAW
        )
        glEnableVertexAttribArray(5)
        glVertexAttribPointer(5, 4, GL_FLOAT, GL_FALSE, 64, ctypes.c_void_p(0))
        glEnableVertexAttribArray(6)
        glVertexAttribPointer(6, 4, GL_FLOAT, GL_FALSE, 64, ctypes.c_void_p(16))
        glEnableVertexAttribArray(7)
        glVertexAttribPointer(7, 4, GL_FLOAT, GL_FALSE, 64, ctypes.c_void_p(32))
        glEnableVertexAttribArray(8)
        glVertexAttribPointer(8, 4, GL_FLOAT, GL_FALSE, 64, ctypes.c_void_p(48))
        glVertexAttribDivisor(5,1)
        glVertexAttribDivisor(6,1)
        glVertexAttribDivisor(7,1)
        glVertexAttribDivisor(8,1)

        self.monkey_mesh = ObjMesh("models/monkey.obj")
        self.monkeyTransforms = np.array([
            pyrr.matrix44.create_identity(dtype = np.float32)
            for i in range(len(scene.monkeys))
        ], dtype=np.float32)
        glBindVertexArray(self.monkey_mesh.vao)
        self.monkeyTransformVBO = glGenBuffers(1)
        glBindBuffer(
            GL_ARRAY_BUFFER, 
            self.monkeyTransformVBO
        )
        glBufferData(
            GL_ARRAY_BUFFER, 
            self.monkeyTransforms.nbytes, 
            self.monkeyTransforms, 
            GL_STATIC_DRAW
        )
        glEnableVertexAttribArray(5)
        glVertexAttribPointer(5, 4, GL_FLOAT, GL_FALSE, 64, ctypes.c_void_p(0))
        glEnableVertexAttribArray(6)
        glVertexAttribPointer(6, 4, GL_FLOAT, GL_FALSE, 64, ctypes.c_void_p(16))
        glEnableVertexAttribArray(7)
        glVertexAttribPointer(7, 4, GL_FLOAT, GL_FALSE, 64, ctypes.c_void_p(32))
        glEnableVertexAttribArray(8)
        glVertexAttribPointer(8, 4, GL_FLOAT, GL_FALSE, 64, ctypes.c_void_p(48))
        glVertexAttribDivisor(5,1)
        glVertexAttribDivisor(6,1)
        glVertexAttribDivisor(7,1)
        glVertexAttribDivisor(8,1)

        glUseProgram(self.shaderLPass)
        self.screenQuad = TexturedQuad(0, 0, 2, 2)

        glUseProgram(self.shaderColored)
        self.light_mesh = UntexturedCubeMesh(
            l = 0.1,
            w = 0.1,
            h = 0.1
        )

    def create_framebuffer(self):

        #geometry buffer
        self.gBuffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.gBuffer)

        #position data
        self.gPosition = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.gPosition)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, 640, 480, 0, GL_RGBA, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, 
                                GL_TEXTURE_2D, self.gPosition, 0)

        #albedo data + specular (RGB albedo, A specular)
        self.gAlbedoSpecular = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.gAlbedoSpecular)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 640, 480, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT1, 
                                GL_TEXTURE_2D, self.gAlbedoSpecular, 0)

        #normal data + ao data (RGB normal, A ao)
        self.gNormalAo = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.gNormalAo)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 640, 480, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT2, 
                                GL_TEXTURE_2D, self.gNormalAo, 0)

        glDrawBuffers(3, (GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1, GL_COLOR_ATTACHMENT2))

        #depth-stencil
        self.gDepthStencil = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, self.gDepthStencil)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, 640, 480)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, 
                                    GL_RENDERBUFFER, self.gDepthStencil)

    def draw(self, scene):
        #refresh screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.prepare_shaders(scene)
        
        self.geometry_pass(scene)

        self.lighting_pass()

        self.draw_lights(scene)

        pg.display.flip()
    
    def prepare_shaders(self, scene):

        #view
        view_transform = pyrr.matrix44.create_look_at(
            eye = scene.player.position,
            target = scene.player.position + scene.player.get_forwards(),
            up = scene.player.get_up(),
            dtype = np.float32
        )

        glUseProgram(self.shaderGPass)
        glUniformMatrix4fv(
            self.viewLocgPass, 1, GL_FALSE, view_transform
        )

        glUseProgram(self.shaderLPass)
        glUniform3fv(self.cameraLocTextured, 1, scene.player.position)

        glUseProgram(self.shaderColored)
        glUniformMatrix4fv(self.viewLocUntextured, 1, GL_FALSE, view_transform)

        #lights
        glUseProgram(self.shaderLPass)
        glUniform1f(self.lightLocTextured["count"], min(8,max(0,len(scene.lights))))

        for i, light in enumerate(scene.lights):
            glUniform3fv(self.lightLocTextured["pos"][i], 1, light.position)
            glUniform3fv(self.lightLocTextured["color"][i], 1, light.color)
            glUniform1f(self.lightLocTextured["strength"][i], 2)
        
        #positions
        glUseProgram(self.shaderGPass)
        
        for i, container in enumerate(scene.containers):
            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform, 
                m2=pyrr.matrix44.create_from_eulers(
                    eulers=np.radians(container.eulers), dtype=np.float32
                )
            )
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform, 
                m2=pyrr.matrix44.create_from_translation(
                    vec=np.array(container.position),dtype=np.float32
                )
            )
            self.containerTransforms[i] = model_transform
        
        glBindVertexArray(self.container_mesh.vao)
        glBindBuffer(
            GL_ARRAY_BUFFER, 
            self.containerTransformVBO
        )
        glBufferData(GL_ARRAY_BUFFER, self.containerTransforms.nbytes, self.containerTransforms, GL_STATIC_DRAW)

        for i, monkey in enumerate(scene.monkeys):
            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform, 
                m2=pyrr.matrix44.create_from_eulers(
                    eulers=np.radians(monkey.eulers), dtype=np.float32
                )
            )
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform, 
                m2=pyrr.matrix44.create_from_translation(
                    vec=np.array(monkey.position),dtype=np.float32
                )
            )
            self.monkeyTransforms[i] = model_transform
        
        glBindVertexArray(self.monkey_mesh.vao)
        glBindBuffer(
            GL_ARRAY_BUFFER, 
            self.monkeyTransformVBO
        )
        glBufferData(GL_ARRAY_BUFFER, self.monkeyTransforms.nbytes, self.monkeyTransforms, GL_STATIC_DRAW)
    
    def geometry_pass(self, scene):

        glUseProgram(self.shaderGPass)
        glBindFramebuffer(GL_FRAMEBUFFER, self.gBuffer)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glDrawBuffers(3, (GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1, GL_COLOR_ATTACHMENT2))
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        self.wood_texture.use()

        glDisable(GL_CULL_FACE)
        glBindVertexArray(self.container_mesh.vao)
        glBindBuffer(
            GL_ARRAY_BUFFER, 
            self.containerTransformVBO
        )
        glDrawArraysInstanced(GL_TRIANGLES, 0, self.container_mesh.vertex_count, len(scene.containers))
        glEnable(GL_CULL_FACE)
        glBindVertexArray(self.monkey_mesh.vao)
        glBindBuffer(
            GL_ARRAY_BUFFER, 
            self.monkeyTransformVBO
        )
        glDrawArraysInstanced(GL_TRIANGLES, 0, self.monkey_mesh.vertex_count, len(scene.monkeys))
    
    def lighting_pass(self):

        glUseProgram(self.shaderLPass)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.gPosition)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.gAlbedoSpecular)
        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_2D, self.gNormalAo)

        glBindVertexArray(self.screenQuad.vao)
        glDrawArrays(GL_TRIANGLES,0,6)

        glBindFramebuffer(GL_READ_FRAMEBUFFER, self.gBuffer)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
        glBlitFramebuffer(0, 0, 640, 480, 0, 0, 640, 480, GL_DEPTH_BUFFER_BIT, GL_NEAREST)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def draw_lights(self, scene):

        glUseProgram(self.shaderColored)
        glDisable(GL_CULL_FACE)
        for light in scene.lights:
            model_transform = pyrr.matrix44.create_from_translation(
                vec=np.array(light.position),dtype=np.float32
            )
            glUniformMatrix4fv(self.modelLocUntextured, 1, GL_FALSE, model_transform)
            glUniform3fv(self.colorLocUntextured, 1, light.color)
            glBindVertexArray(self.light_mesh.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.light_mesh.vertex_count)

    def quit(self):
        self.container_mesh.destroy()
        self.monkey_mesh.destroy()
        self.light_mesh.destroy()
        self.wood_texture.destroy()
        self.screenQuad.destroy()
        glDeleteBuffers(2, (self.containerTransformVBO,self.monkeyTransformVBO))
        glDeleteFramebuffers(1, (self.gBuffer,))
        glDeleteTextures(3, (self.gPosition, self.gAlbedoSpecular, self.gNormalAo))
        glDeleteProgram(self.shaderGPass)
        glDeleteProgram(self.shaderLPass)
        glDeleteProgram(self.shaderColored)
        pg.quit()

class Material:

    def __init__(self, filename, filetype):

        self.textures = []

        #albedo : 0
        self.textures.append(glGenTextures(1))
        glBindTexture(GL_TEXTURE_2D, self.textures[0])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(f"gfx\{filename}_albedo.{filetype}").convert()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)
        
        #ambient occlusion : 1
        self.textures.append(glGenTextures(1))
        glBindTexture(GL_TEXTURE_2D, self.textures[1])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(f"gfx\{filename}_ao.{filetype}").convert()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        #normal : 2
        self.textures.append(glGenTextures(1))
        glBindTexture(GL_TEXTURE_2D, self.textures[2])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(f"gfx\{filename}_normal.{filetype}").convert()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        #specular : 3
        self.textures.append(glGenTextures(1))
        glBindTexture(GL_TEXTURE_2D, self.textures[3])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(f"gfx\{filename}_normal.{filetype}").convert()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):

        for i in range(len(self.textures)):
            glActiveTexture(GL_TEXTURE0 + i)
            glBindTexture(GL_TEXTURE_2D,self.textures[i])
    
    def destroy(self):
        glDeleteTextures(len(self.textures), self.textures)

class UntexturedCubeMesh:


    def __init__(self, l, w, h):
        # x, y, z
        self.vertices = (
                -l/2, -w/2, -h/2,
                 l/2, -w/2, -h/2,
                 l/2,  w/2, -h/2,

                 l/2,  w/2, -h/2,
                -l/2,  w/2, -h/2,
                -l/2, -w/2, -h/2,

                -l/2, -w/2,  h/2,
                 l/2, -w/2,  h/2,
                 l/2,  w/2,  h/2,

                 l/2,  w/2,  h/2,
                -l/2,  w/2,  h/2,
                -l/2, -w/2,  h/2,

                -l/2,  w/2,  h/2,
                -l/2,  w/2, -h/2,
                -l/2, -w/2, -h/2,

                -l/2, -w/2, -h/2,
                -l/2, -w/2,  h/2,
                -l/2,  w/2,  h/2,

                 l/2,  w/2,  h/2,
                 l/2,  w/2, -h/2,
                 l/2, -w/2, -h/2,

                 l/2, -w/2, -h/2,
                 l/2, -w/2,  h/2,
                 l/2,  w/2,  h/2,

                -l/2, -w/2, -h/2,
                 l/2, -w/2, -h/2,
                 l/2, -w/2,  h/2,

                 l/2, -w/2,  h/2,
                -l/2, -w/2,  h/2,
                -l/2, -w/2, -h/2,

                -l/2,  w/2, -h/2,
                 l/2,  w/2, -h/2,
                 l/2,  w/2,  h/2,

                 l/2,  w/2,  h/2,
                -l/2,  w/2,  h/2,
                -l/2,  w/2, -h/2
            )
        self.vertex_count = len(self.vertices)//3
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class ObjMesh:

    def __init__(self, filename):
        # x, y, z, s, t, nx, ny, nz, tangent, bitangent, model(instanced)
        self.vertices = self.loadMesh(filename)
        self.vertex_count = len(self.vertices)//14
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        offset = 0
        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
        #texture
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 8
        #normal
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
        #tangent
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
        #bitangent
        glEnableVertexAttribArray(4)
        glVertexAttribPointer(4, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
    
    def loadMesh(self, filename):

        #raw, unassembled data
        v = []
        vt = []
        vn = []
        
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
                    #face, three or more vertices in v/vt/vn form
                    line = line.replace("f ","")
                    line = line.replace("\n","")
                    #get the individual vertices for each line
                    line = line.split(" ")
                    faceVertices = []
                    faceTextures = []
                    faceNormals = []
                    for vertex in line:
                        #break out into [v,vt,vn],
                        #correct for 0 based indexing.
                        l = vertex.split("/")
                        position = int(l[0]) - 1
                        faceVertices.append(v[position])
                        texture = int(l[1]) - 1
                        faceTextures.append(vt[texture])
                        normal = int(l[2]) - 1
                        faceNormals.append(vn[normal])
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
                    # calculate tangent and bitangent for point
                    # how do model positions relate to texture positions?
                    point1 = faceVertices[vertex_order[0]]
                    point2 = faceVertices[vertex_order[1]]
                    point3 = faceVertices[vertex_order[2]]
                    uv1 = faceTextures[vertex_order[0]]
                    uv2 = faceTextures[vertex_order[1]]
                    uv3 = faceTextures[vertex_order[2]]
                    #direction vectors
                    deltaPos1 = [point2[i] - point1[i] for i in range(3)]
                    deltaPos2 = [point3[i] - point1[i] for i in range(3)]
                    deltaUV1 = [uv2[i] - uv1[i] for i in range(2)]
                    deltaUV2 = [uv3[i] - uv1[i] for i in range(2)]
                    # calculate
                    den = 1 / (deltaUV1[0] * deltaUV2[1] - deltaUV2[0] * deltaUV1[1])
                    tangent = []
                    #tangent x
                    tangent.append(den * (deltaUV2[1] * deltaPos1[0] - deltaUV1[1] * deltaPos2[0]))
                    #tangent y
                    tangent.append(den * (deltaUV2[1] * deltaPos1[1] - deltaUV1[1] * deltaPos2[1]))
                    #tangent z
                    tangent.append(den * (deltaUV2[1] * deltaPos1[2] - deltaUV1[1] * deltaPos2[2]))
                    bitangent = []
                    #bitangent x
                    bitangent.append(den * (-deltaUV2[0] * deltaPos1[0] + deltaUV1[0] * deltaPos2[0]))
                    #bitangent y
                    bitangent.append(den * (-deltaUV2[0] * deltaPos1[1] + deltaUV1[0] * deltaPos2[1]))
                    #bitangent z
                    bitangent.append(den * (-deltaUV2[0] * deltaPos1[2] + deltaUV1[0] * deltaPos2[2]))
                    for i in vertex_order:
                        for x in faceVertices[i]:
                            vertices.append(x)
                        for x in faceTextures[i]:
                            vertices.append(x)
                        for x in faceNormals[i]:
                            vertices.append(x)
                        for x in tangent:
                            vertices.append(x)
                        for x in bitangent:
                            vertices.append(x)
                line = f.readline()
        return vertices
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))

class TexturedQuad:


    def __init__(self, x, y, w, h):

        self.vertices = (
            x - w/2, y + h/2, 0, 1,
            x - w/2, y - h/2, 0, 0,
            x + w/2, y - h/2, 1, 0,

            x - w/2, y + h/2, 0, 1,
            x + w/2, y - h/2, 1, 0,
            x + w/2, y + h/2, 1, 1
        )
        self.vertices = np.array(self.vertices, dtype=np.float32)
        
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(8))
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

###############################################################################

myApp = App()