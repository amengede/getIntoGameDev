import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
import random

##################################### Model ###################################

class Cube:


    def __init__(self, position, eulers, eulerVelocity):

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)
        self.eulerVelocity = np.array(eulerVelocity, dtype=np.float32)

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

        self.cubes = [
            Cube(
                position = [random.uniform(a = -10, b = 10) for x in range(3)],
                eulers = [random.uniform(a = 0, b = 360) for x in range(3)],
                eulerVelocity = [random.uniform(a = -0.1, b = 0.1) for x in range(3)]
            )

            for i in range(200)
        ]

        self.lights = [
            Light(
                position = [random.uniform(a = -10, b = 10) for x in range(3)],
                color = [random.uniform(a = 0.5, b = 1) for x in range(3)]
            )

            for i in range(8)
        ]

        self.player = Player(
            position = [-10, 0, 0],
            eulers = [0, 0, 0]
        )
    
    def update(self):

        for cube in self.cubes:
            cube.eulers = np.mod(
                cube.eulers + cube.eulerVelocity, 
                [360, 360, 360], 
                dtype=np.float32
            )

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
        self.shaderTextured = self.createShader(
            "shaders/vertex.txt", 
            "shaders/fragment.txt"
        )
        self.shaderColored = self.createShader(
            "shaders/simple_3d_vertex.txt", 
            "shaders/simple_3d_fragment.txt"
        )
        
        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = 640/480, 
            near = 0.1, far = 40, dtype=np.float32
        )

        glUseProgram(self.shaderTextured)
        #get shader locations
        self.viewLocTextured = glGetUniformLocation(self.shaderTextured, "view")
        self.lightLocTextured = {

            "pos": [
                glGetUniformLocation(
                    self.shaderTextured,f"lightPos[{i}]"
                ) 
                for i in range(8)
            ],

            "color": [
                glGetUniformLocation(
                    self.shaderTextured,f"lights[{i}].color"
                ) 
                for i in range(8)
            ],

            "strength": [
                glGetUniformLocation(
                    self.shaderTextured,f"lights[{i}].strength"
                ) 
                for i in range(8)
            ],

            "count": glGetUniformLocation(
                self.shaderTextured,f"lightCount"
            )
        }

        self.cameraLocTextured = glGetUniformLocation(self.shaderTextured, "viewPos")

        #set up uniforms
        glUniformMatrix4fv(
            glGetUniformLocation(
                self.shaderTextured,"projection"
            ),
            1,GL_FALSE,projection_transform
        )

        glUniform3fv(
            glGetUniformLocation(
                self.shaderTextured,"ambient"
            ), 
            1, np.array([0.1, 0.1, 0.1],dtype=np.float32)
        )

        glUniform1i(
            glGetUniformLocation(
                self.shaderTextured, "material.albedo"
            ), 0
        )

        glUniform1i(
            glGetUniformLocation(
                self.shaderTextured, "material.ao"
            ), 1
        )

        glUniform1i(
            glGetUniformLocation(
                self.shaderTextured, "material.normal"
            ), 2
        )

        glUniform1i(
            glGetUniformLocation(
                self.shaderTextured, "material.specular"
            ), 3
        )
        #create assets
        self.wood_texture = Material("crate", "png")
        self.cube_mesh = ObjMesh("models/cube.obj")
        #generate position buffer
        self.cubeTransforms = np.array([
            pyrr.matrix44.create_identity(dtype = np.float32)

            for i in range(len(scene.cubes))
        ], dtype=np.float32)
        glBindVertexArray(self.cube_mesh.vao)
        self.cubeTransformVBO = glGenBuffers(1)
        glBindBuffer(
            GL_ARRAY_BUFFER, 
            self.cubeTransformVBO
        )
        glBufferData(
            GL_ARRAY_BUFFER, 
            self.cubeTransforms.nbytes, 
            self.cubeTransforms, 
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

        glUseProgram(self.shaderColored)
        #get shader locations
        self.viewLocUntextured = glGetUniformLocation(self.shaderColored, "view")
        self.modelLocUntextured = glGetUniformLocation(self.shaderColored, "model")
        self.colorLocUntextured = glGetUniformLocation(self.shaderColored, "color")

        glUniformMatrix4fv(
            glGetUniformLocation(
                self.shaderColored,"projection"
            ),1,GL_FALSE,projection_transform
        )

        #create assets
        self.light_mesh = UntexturedCubeMesh(
            l = 0.1,
            w = 0.1,
            h = 0.1
        )

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

    def draw(self, scene):
        #refresh screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        view_transform = pyrr.matrix44.create_look_at(
            eye = scene.player.position,
            target = scene.player.position + scene.player.get_forwards(),
            up = scene.player.get_up(),
            dtype = np.float32
        )

        glUseProgram(self.shaderTextured)
        glUniformMatrix4fv(
            self.viewLocTextured, 1, GL_FALSE, view_transform
        )
        glUniform3fv(self.cameraLocTextured, 1, scene.player.position)
        #lights
        glUniform1f(self.lightLocTextured["count"], min(8,max(0,len(scene.lights))))

        for i, light in enumerate(scene.lights):
            glUniform3fv(self.lightLocTextured["pos"][i], 1, light.position)
            glUniform3fv(self.lightLocTextured["color"][i], 1, light.color)
            glUniform1f(self.lightLocTextured["strength"][i], 1)
        
        for i, cube in enumerate(scene.cubes):
            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform, 
                m2=pyrr.matrix44.create_from_eulers(
                    eulers=np.radians(cube.eulers), dtype=np.float32
                )
            )
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform, 
                m2=pyrr.matrix44.create_from_translation(
                    vec=np.array(cube.position),dtype=np.float32
                )
            )
            self.cubeTransforms[i] = model_transform
        
        glBindVertexArray(self.cube_mesh.vao)
        glBindBuffer(
            GL_ARRAY_BUFFER, 
            self.cubeTransformVBO
        )
        glBufferData(GL_ARRAY_BUFFER, self.cubeTransforms.nbytes, self.cubeTransforms, GL_STATIC_DRAW)
        self.wood_texture.use()
        glDrawArraysInstanced(GL_TRIANGLES, 0, self.cube_mesh.vertex_count, len(scene.cubes))
        
        glUseProgram(self.shaderColored)
        
        glUniformMatrix4fv(self.viewLocUntextured, 1, GL_FALSE, view_transform)

        for light in scene.lights:
            model_transform = pyrr.matrix44.create_from_translation(
                vec=np.array(light.position),dtype=np.float32
            )
            glUniformMatrix4fv(self.modelLocUntextured, 1, GL_FALSE, model_transform)
            glUniform3fv(self.colorLocUntextured, 1, light.color)
            glBindVertexArray(self.light_mesh.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.light_mesh.vertex_count)

        pg.display.flip()

    def quit(self):
        self.cube_mesh.destroy()
        self.light_mesh.destroy()
        self.wood_texture.destroy()
        glDeleteBuffers(1, (self.cubeTransformVBO,))
        glDeleteProgram(self.shaderTextured)
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

###############################################################################

myApp = App()