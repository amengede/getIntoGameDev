import pygame as pg
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
import ctypes

############################## Constants ######################################

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

CONTINUE = 0
NEW_GAME = 1
OPEN_MENU = 2
EXIT = 3

FONT_TEX_COORDS = {
    "!" :  [1.0/32,  15.0/16, 2.0/32,  14.0/16],
    "\"" : [2.0/32,  15.0/16, 3.0/32,  14.0/16],
    "#" :  [3.0/32,  15.0/16, 4.0/32,  14.0/16],
    "$" :  [4.0/32,  15.0/16, 5.0/32,  14.0/16],
    "%" :  [5.0/32,  15.0/16, 6.0/32,  14.0/16],
    "&" :  [6.0/32,  15.0/16, 7.0/32,  14.0/16],
    "\'" : [7.0/32,  15.0/16, 8.0/32,  14.0/16],
    "(" :  [8.0/32,  15.0/16, 9.0/32,  14.0/16],
    ")" :  [9.0/32,  15.0/16, 10.0/32, 14.0/16],
    "*" :  [10.0/32, 15.0/16, 11.0/32, 14.0/16],
    "+" :  [11.0/32, 15.0/16, 12.0/32, 14.0/16],
    "," :  [12.0/32, 15.0/16, 13.0/32, 14.0/16],
    "-" :  [13.0/32, 15.0/16, 14.0/32, 14.0/16],
    "." :  [14.0/32, 15.0/16, 15.0/32, 14.0/16],
    "/" :  [15.0/32, 15.0/16, 16.0/32, 14.0/16],
    "0" :  [16.0/32, 15.0/16, 17.0/32, 14.0/16],
    "1" :  [17.0/32, 15.0/16, 18.0/32, 14.0/16],
    "2" :  [18.0/32, 15.0/16, 19.0/32, 14.0/16],
    "3" :  [19.0/32, 15.0/16, 20.0/32, 14.0/16],
    "4" :  [20.0/32, 15.0/16, 21.0/32, 14.0/16],
    "5" :  [21.0/32, 15.0/16, 22.0/32, 14.0/16],
    "6" :  [22.0/32, 15.0/16, 23.0/32, 14.0/16],
    "7" :  [23.0/32, 15.0/16, 24.0/32, 14.0/16],
    "8" :  [24.0/32, 15.0/16, 25.0/32, 14.0/16],
    "9" :  [25.0/32, 15.0/16, 26.0/32, 14.0/16],
    ":" :  [26.0/32, 15.0/16, 27.0/32, 14.0/16],
    ";" :  [27.0/32, 15.0/16, 28.0/32, 14.0/16],
    "<" :  [28.0/32, 15.0/16, 29.0/32, 14.0/16],
    "=" :  [29.0/32, 15.0/16, 30.0/32, 14.0/16],
    ">" :  [30.0/32, 15.0/16, 31.0/32, 14.0/16],
    "?" :  [31.0/32, 15.0/16, 32.0/32, 14.0/16],

    "@" :  [0.0,     14.0/16, 1.0/32,  13.0/16],
    "A" :  [1.0/32,  14.0/16, 2.0/32,  13.0/16],
    "B" :  [2.0/32,  14.0/16, 3.0/32,  13.0/16],
    "C" :  [3.0/32,  14.0/16, 4.0/32,  13.0/16],
    "D" :  [4.0/32,  14.0/16, 5.0/32,  13.0/16],
    "E" :  [5.0/32,  14.0/16, 6.0/32,  13.0/16],
    "F" :  [6.0/32,  14.0/16, 7.0/32,  13.0/16],
    "G" :  [7.0/32,  14.0/16, 8.0/32,  13.0/16],
    "H" :  [8.0/32,  14.0/16, 9.0/32,  13.0/16],
    "I" :  [9.0/32,  14.0/16, 10.0/32, 13.0/16],
    "J" :  [10.0/32, 14.0/16, 11.0/32, 13.0/16],
    "K" :  [11.0/32, 14.0/16, 12.0/32, 13.0/16],
    "L" :  [12.0/32, 14.0/16, 13.0/32, 13.0/16],
    "M" :  [13.0/32, 14.0/16, 14.0/32, 13.0/16],
    "N" :  [14.0/32, 14.0/16, 15.0/32, 13.0/16],
    "O" :  [15.0/32, 14.0/16, 16.0/32, 13.0/16],
    "P" :  [16.0/32, 14.0/16, 17.0/32, 13.0/16],
    "Q" :  [17.0/32, 14.0/16, 18.0/32, 13.0/16],
    "R" :  [18.0/32, 14.0/16, 19.0/32, 13.0/16],
    "S" :  [19.0/32, 14.0/16, 20.0/32, 13.0/16],
    "T" :  [20.0/32, 14.0/16, 21.0/32, 13.0/16],
    "U" :  [21.0/32, 14.0/16, 22.0/32, 13.0/16],
    "V" :  [22.0/32, 14.0/16, 23.0/32, 13.0/16],
    "W" :  [23.0/32, 14.0/16, 24.0/32, 13.0/16],
    "X" :  [24.0/32, 14.0/16, 25.0/32, 13.0/16],
    "Y" :  [25.0/32, 14.0/16, 26.0/32, 13.0/16],
    "Z" :  [26.0/32, 14.0/16, 27.0/32, 13.0/16],
    "[" :  [27.0/32, 14.0/16, 28.0/32, 13.0/16],
    "\\" : [28.0/32, 14.0/16, 29.0/32, 13.0/16],
    "]" :  [29.0/32, 14.0/16, 30.0/32, 13.0/16],
    "^" :  [30.0/32, 14.0/16, 31.0/32, 13.0/16],
    "_" :  [31.0/32, 14.0/16, 32.0/32, 13.0/16],

    "`" :  [0.0,     13.0/16, 1.0/32,  12.0/16],
    "a" :  [1.0/32,  13.0/16, 2.0/32,  12.0/16],
    "b" :  [2.0/32,  13.0/16, 3.0/32,  12.0/16],
    "c" :  [3.0/32,  13.0/16, 4.0/32,  12.0/16],
    "d" :  [4.0/32,  13.0/16, 5.0/32,  12.0/16],
    "e" :  [5.0/32,  13.0/16, 6.0/32,  12.0/16],
    "f" :  [6.0/32,  13.0/16, 7.0/32,  12.0/16],
    "g'" : [7.0/32,  13.0/16, 8.0/32,  12.0/16],
    "h" :  [8.0/32,  13.0/16, 9.0/32,  12.0/16],
    "i" :  [9.0/32,  13.0/16, 10.0/32, 12.0/16],
    "j" :  [10.0/32, 13.0/16, 11.0/32, 12.0/16],
    "k" :  [11.0/32, 13.0/16, 12.0/32, 12.0/16],
    "l" :  [12.0/32, 13.0/16, 13.0/32, 12.0/16],
    "m" :  [13.0/32, 13.0/16, 14.0/32, 12.0/16],
    "n" :  [14.0/32, 13.0/16, 15.0/32, 12.0/16],
    "o" :  [15.0/32, 13.0/16, 16.0/32, 12.0/16],
    "p" :  [16.0/32, 13.0/16, 17.0/32, 12.0/16],
    "q" :  [17.0/32, 13.0/16, 18.0/32, 12.0/16],
    "r" :  [18.0/32, 13.0/16, 19.0/32, 12.0/16],
    "s" :  [19.0/32, 13.0/16, 20.0/32, 12.0/16],
    "t" :  [20.0/32, 13.0/16, 21.0/32, 12.0/16],
    "u" :  [21.0/32, 13.0/16, 22.0/32, 12.0/16],
    "v" :  [22.0/32, 13.0/16, 23.0/32, 12.0/16],
    "w" :  [23.0/32, 13.0/16, 24.0/32, 12.0/16],
    "x" :  [24.0/32, 13.0/16, 25.0/32, 12.0/16],
    "y" :  [25.0/32, 13.0/16, 26.0/32, 12.0/16],
    "z" :  [26.0/32, 13.0/16, 27.0/32, 12.0/16],
    "{" :  [27.0/32, 13.0/16, 28.0/32, 12.0/16],
    "|" :  [28.0/32, 13.0/16, 29.0/32, 12.0/16],
    "}" :  [29.0/32, 13.0/16, 30.0/32, 12.0/16]
}

############################## helper functions ###############################

def initialise_pygame():
    pg.init()
    pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
    pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
    pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                pg.GL_CONTEXT_PROFILE_CORE)
    pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.OPENGL|pg.DOUBLEBUF)
    pg.mouse.set_pos((SCREEN_HEIGHT / 2, SCREEN_HEIGHT / 2))

def initialise_opengl():
    glClearColor(0.1, 0.1, 0.1, 1)
    shader3DTextured = createShader("shaders/vertex_3d_textured.txt",
                                        "shaders/fragment_3d_textured.txt")
    shader3DColored = createShader("shaders/vertex_3d_colored.txt",
                                            "shaders/fragment_3d_colored.txt")
    shader2DTextured = createShader("shaders/vertex_2d_textured.txt",
                                        "shaders/fragment_2d_textured.txt")
    shader2DColored = createShader("shaders/vertex_2d_colored.txt",
                                            "shaders/fragment_2d_colored.txt")
    shader2DText = createShader("shaders/vertex_2d_textured.txt",
                                            "shaders/fragment_text.txt")

    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    projection_transform = pyrr.matrix44.create_perspective_projection(45, SCREEN_WIDTH/SCREEN_HEIGHT, 
                                                                        0.1, 10, dtype=np.float32)
    
    glUseProgram(shader3DTextured)
    glUniformMatrix4fv(glGetUniformLocation(shader3DTextured,"projection"),1,GL_FALSE,projection_transform)
    glUniform3fv(glGetUniformLocation(shader3DTextured,"ambient"), 1, np.array([0.1, 0.1, 0.1],dtype=np.float32))
    glUniform1i(glGetUniformLocation(shader3DTextured, "material.diffuse"), 0)
    glUniform1i(glGetUniformLocation(shader3DTextured, "material.specular"), 1)

    glUseProgram(shader3DColored)
    glUniformMatrix4fv(glGetUniformLocation(shader3DColored,"projection"),1,GL_FALSE,projection_transform)
    return (shader3DTextured, shader3DColored, shader2DTextured, shader2DColored, shader2DText)

def createShader(vertexFilepath, fragmentFilepath):

        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        return shader

def create_framebuffer():
        fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)
        
        colorBuffer = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, colorBuffer)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 640, 480, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, 
                                GL_TEXTURE_2D, colorBuffer, 0)
        
        depthStencilBuffer = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, depthStencilBuffer)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, 640, 480)
        glBindRenderbuffer(GL_RENDERBUFFER,0)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, 
                                    GL_RENDERBUFFER, depthStencilBuffer)

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        return (fbo, colorBuffer, depthStencilBuffer)

def teardown_program_environment(shaders, framebuffer):
    (fbo, colorBuffer, depthStencilBuffer) = framebuffer
    glDeleteTextures(1,(colorBuffer,))
    glDeleteRenderbuffers(1, (depthStencilBuffer,))
    glDeleteFramebuffers(1,(fbo,))
    for shader in shaders:
        glDeleteProgram(shader)
    pg.quit()

############################## model ##########################################

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

    def update(self):
        glUseProgram(self.shader)
        angle = np.radians((20*(pg.time.get_ticks()/1000))%360)
        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        #model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_z_rotation(theta=angle,dtype=np.float32))
        model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_translation(vec=np.array(self.position),dtype=np.float32))
        glUniformMatrix4fv(glGetUniformLocation(self.shader,"model"),1,GL_FALSE,model_transform)

    def draw(self):
        glUseProgram(self.shader)
        self.material.use()
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

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

class SimpleMaterial:
    def __init__(self, filepath):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(f"{filepath}.png").convert_alpha()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA8,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.texture)

    def destroy(self):
        glDeleteTextures(1, (self.texture,))

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

class TexturedQuad:
    def __init__(self, x, y, w, h, texture, shader):
        self.shader = shader
        self.texture = texture
        self.vertices = (
            x - w/2, y + h/2, 0, 1,
            x - w/2, y - h/2, 0, 0,
            x + w/2, y - h/2, 1, 0,

            x - w/2, y + h/2, 0, 1,
            x + w/2, y - h/2, 1, 0,
            x + w/2, y + h/2, 1, 1
        )
        self.vertices = np.array(self.vertices, dtype=np.float32)
        
        glUseProgram(self.shader)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(8))
    
    def draw(self):
        glUseProgram(self.shader)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES,0,6)
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

############################## gui ############################################

def new_game_click():
    return NEW_GAME

def exit_click():
    return EXIT

class Button:
    def __init__(self, pos, size, color, shader):
        self.clickAction = None
        self.label = None
        self.pos = pos
        self.size = size
        self.color = color
        self.invertedColor = [0,0,0]
        for channel in range(3):
            self.invertedColor[channel] = abs(1 - self.color[channel])
        self.shader = shader

        self.vertices = (
            pos[0] - size[0]/2, pos[1] + size[1]/2, color[0], color[1], color[2],
            pos[0] - size[0]/2, pos[1] - size[1]/2, color[0], color[1], color[2],
            pos[0] + size[0]/2, pos[1] - size[1]/2, color[0], color[1], color[2],

            pos[0] - size[0]/2, pos[1] + size[1]/2, color[0], color[1], color[2],
            pos[0] + size[0]/2, pos[1] - size[1]/2, color[0], color[1], color[2],
            pos[0] + size[0]/2, pos[1] + size[1]/2, color[0], color[1], color[2]
        )
        self.vertices = np.array(self.vertices, dtype=np.float32)
        
        glUseProgram(self.shader)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(8))
    
    def inside(self, pos):
        for i in range(2):
            if pos[i] < (self.pos[i] - self.size[i]) or pos[i] > (self.pos[i] + self.size[i]):
                return False
        return True
    
    def handle_mouse_movement(self, pos):
        if self.inside(pos):
            newColor = self.invertedColor
            if self.label is not None:
                self.label.color = np.array(self.color,dtype=np.float32)
        else:
            newColor = self.color
            if self.label is not None:
                self.label.color = np.array(self.color,dtype=np.float32)
        
        for i in range(6):
            self.vertices[5 * i + 2] = newColor[0]
            self.vertices[5 * i + 3] = newColor[1]
            self.vertices[5 * i + 4] = newColor[2]
        
        glBindBuffer(GL_ARRAY_BUFFER,self.vbo)
        memoryHandle = glMapBuffer(GL_ARRAY_BUFFER, GL_WRITE_ONLY)
        ctypes.memmove(ctypes.c_void_p(memoryHandle), ctypes.c_void_p(self.vertices.ctypes.data), self.vertices.nbytes)
        glUnmapBuffer(GL_ARRAY_BUFFER)
    
    def handle_mouse_click(self, pos):
        if self.inside(pos):
            if self.clickAction is not None:
                return self.clickAction()
        return CONTINUE

    def draw(self):
        glUseProgram(self.shader)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES,0,6)
    
    def destroy(self):
        glDeleteBuffers(1, (self.vbo,))
        glDeleteVertexArrays(1, (self.vao,))

class TextLine:
    def __init__(self, font, text, shader, fontsize, startPos, color):
        self.font = font
        self.text = text
        self.shader = shader
        self.vertices = []
        self.vertexCount = 0
        self.fontsize = fontsize
        self.startPos = startPos
        self.color = np.array(color, dtype=np.float32)

        glUseProgram(self.shader)
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.build_text()

    def build_text(self):
        self.vertices = []
        self.vertexCount = 0

        for i in range(len(self.text)):
            character = self.text[i]
            if character in FONT_TEX_COORDS:
                #top left pos
                self.vertices.append(self.startPos[0] + i * self.fontsize[0])
                self.vertices.append(self.startPos[1] + self.fontsize[1])
                #top left tex coord
                self.vertices.append(FONT_TEX_COORDS[character][0])
                self.vertices.append(FONT_TEX_COORDS[character][1] - 0.15/16)
                #top right pos
                self.vertices.append(self.startPos[0] + (i + 1) * self.fontsize[0])
                self.vertices.append(self.startPos[1] + self.fontsize[1])
                #top right tex coord
                self.vertices.append(FONT_TEX_COORDS[character][2])
                self.vertices.append(FONT_TEX_COORDS[character][1] - 0.15/16)
                #bottom right pos
                self.vertices.append(self.startPos[0] + (i + 1) * self.fontsize[0])
                self.vertices.append(self.startPos[1] - self.fontsize[1])
                #bottom right tex coord
                self.vertices.append(FONT_TEX_COORDS[character][2])
                self.vertices.append(FONT_TEX_COORDS[character][3] - 0.15/16)

                #bottom right pos
                self.vertices.append(self.startPos[0] + (i + 1) * self.fontsize[0])
                self.vertices.append(self.startPos[1] - self.fontsize[1])
                #bottom right tex coord
                self.vertices.append(FONT_TEX_COORDS[character][2])
                self.vertices.append(FONT_TEX_COORDS[character][3] - 0.15/16)
                #bottom left pos
                self.vertices.append(self.startPos[0] + i * self.fontsize[0])
                self.vertices.append(self.startPos[1] - self.fontsize[1])
                #bottom left tex coord
                self.vertices.append(FONT_TEX_COORDS[character][0])
                self.vertices.append(FONT_TEX_COORDS[character][3] - 0.15/16)
                #top left pos
                self.vertices.append(self.startPos[0] + i * self.fontsize[0])
                self.vertices.append(self.startPos[1] + self.fontsize[1])
                #top left tex coord
                self.vertices.append(FONT_TEX_COORDS[character][0])
                self.vertices.append(FONT_TEX_COORDS[character][1] - 0.15/16)
                self.vertexCount += 6

        self.vertices = np.array(self.vertices,dtype=np.float32)
        glUseProgram(self.shader)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(8))

    def draw(self):
        glUseProgram(self.shader)
        self.font.use()
        glUniform3fv(glGetUniformLocation(self.shader, "color"), 1, self.color)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertexCount)

    def destroy(self):
        glDeleteBuffers(1, (self.vbo,))
        glDeleteVertexArrays(1, (self.vao,))

############################## control ########################################

class GameApp:
    def __init__(self):
        global shaders
        global framebuffer

        self.shader3DTextured = shaders[0]
        self.shader3DColored = shaders[1]
        self.shader2DTextured = shaders[2]

        self.fbo = framebuffer[0]
        self.colorBuffer = framebuffer[1]
        self.depthStencilBuffer = framebuffer[2]

        pg.mouse.set_visible(False)
        self.lastTime = 0
        self.currentTime = 0
        self.numFrames = 0
        self.frameTime = 0
        self.lightCount = 0
        self.resetLights()
        self.create_objects()

    def create_objects(self):
        self.wood_texture = Material("gfx/crate")
        monkey_model = ObjModel("models", "monkey.obj", self.shader3DTextured, self.wood_texture)
        self.monkey = Monkey(np.array([0,0,0],dtype=np.float32), monkey_model)
        self.cube = Cube(self.shader3DTextured, self.wood_texture,[1,1,0.5])
        self.player = Player([0,0,1.2])
        self.light = Light([self.shader3DColored, self.shader3DTextured], [0.2, 0.7, 0.8], [1,1.7,1.5], 2, self.lightCount)
        self.lightCount += 1
        self.light2 = Light([self.shader3DColored, self.shader3DTextured], [0.9, 0.4, 0.0], [0,1.7,0.5], 2, self.lightCount)
        self.lightCount += 1
        self.screen = TexturedQuad(0, 0, 2, 2, self.colorBuffer, self.shader2DTextured)
        self.hud_texture = SimpleMaterial("gfx/hud")
        self.hud = TexturedQuad(0, 0, 2, 2, self.hud_texture.texture, self.shader2DTextured)

    def resetLights(self):
        glUseProgram(self.shader3DTextured)
        for i in range(8):
            glUniform1i(glGetUniformLocation(self.shader3DTextured,f"lights[{i}].enabled"),0)

    def mainLoop(self):
        result = CONTINUE
        #check events
        for event in pg.event.get():
            if (event.type == pg.KEYDOWN and event.key==pg.K_ESCAPE):
                result = EXIT
            if (event.type == pg.KEYDOWN and event.key==pg.K_m):
                result = OPEN_MENU
        self.handleMouse()
        self.handleKeys()
        #update objects
        self.cube.update()
        self.light.update()
        self.light2.update()
        self.player.update([self.shader3DColored, self.shader3DTextured])

        #first pass
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        self.cube.draw()
        self.light.draw()
        self.light2.draw()
        self.monkey.draw()

        #second pass
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClear(GL_COLOR_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)
        self.screen.draw()
        self.hud.draw()
        pg.display.flip()
        #timing
        self.showFrameRate()
        return result

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
        theta_increment = self.frameTime * 0.05 * (SCREEN_WIDTH / 2 - x)
        phi_increment = self.frameTime * 0.05 * (SCREEN_HEIGHT / 2 - y)
        self.player.increment_direction(theta_increment, phi_increment)
        pg.mouse.set_pos((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))

    def showFrameRate(self):
        self.currentTime = pg.time.get_ticks()
        delta = self.currentTime - self.lastTime
        if (delta >= 1000):
            framerate = int(1000.0 * self.numFrames/delta)
            pg.display.set_caption(f"Running at {framerate} fps.")
            self.lastTime = self.currentTime
            self.numFrames = -1
            self.frameTime = float(1000.0 / max(60,framerate))
        self.numFrames += 1

    def quit(self):
        self.wood_texture.destroy()
        self.monkey.destroy()
        self.cube.destroy()
        self.light.destroy()
        self.light2.destroy()
        self.cube.destroy()
        self.screen.destroy()

class MenuApp:
    def __init__(self):
        global shaders

        self.shader2DColored = shaders[3]
        self.shaderText = shaders[4]

        pg.mouse.set_visible(True)
        self.lastTime = 0
        self.currentTime = 0
        self.numFrames = 0
        self.frameTime = 0
        self.create_objects()

    def create_objects(self):

        self.font = SimpleMaterial("gfx/font")

        self.textLines = []

        newgame_label = TextLine(self.font, "New Game", self.shaderText, [0.04, 0.04], [-0.15, 0.3], [0,0,0])
        self.textLines.append(newgame_label)
        exit_label = TextLine(self.font, "Exit", self.shaderText, [0.04, 0.04], [-0.15, -0.3], [0,0,0])
        self.textLines.append(exit_label)
        title = TextLine(self.font, "Monke Madness", self.shaderText, [0.08, 0.08], [-0.5, 0.7], [1,0,0])
        self.textLines.append(title)

        self.buttons = []

        newgame_button = Button((0,0.3), (0.4, 0.1), (1, 1, 0), self.shader2DColored)
        newgame_button.clickAction = new_game_click
        newgame_button.label = newgame_label
        self.buttons.append(newgame_button)

        exit_button = Button((0,-0.3), (0.4, 0.1), (1, 1, 0), self.shader2DColored)
        exit_button.clickAction = exit_click
        exit_button.label = exit_label
        self.buttons.append(exit_button)

    def mainLoop(self):
        result = CONTINUE
        #check events
        for event in pg.event.get():
            if (event.type == pg.MOUSEBUTTONDOWN and event.button==1):
                result = self.handleMouseClick()
            if (event.type == pg.KEYDOWN and event.key==pg.K_ESCAPE):
                result = EXIT
        self.handleMouseMove()
        #render
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClear(GL_COLOR_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        for button in self.buttons:
            button.draw()
        for line in self.textLines:
            line.draw()
        pg.display.flip()

        #timing
        self.showFrameRate()
        return result

    def handleMouseMove(self):
        (x,y) = pg.mouse.get_pos()
        x -= SCREEN_WIDTH / 2
        x /= SCREEN_WIDTH / 2
        y -= SCREEN_HEIGHT / 2
        y /= -SCREEN_HEIGHT / 2

        for button in self.buttons:
            button.handle_mouse_movement((x,y))
    
    def handleMouseClick(self):
        (x,y) = pg.mouse.get_pos()
        x -= SCREEN_WIDTH / 2
        x /= SCREEN_WIDTH / 2
        y -= SCREEN_HEIGHT / 2
        y /= -SCREEN_HEIGHT / 2

        for button in self.buttons:
            result = button.handle_mouse_click((x,y))
            if result != CONTINUE:
                return result
        return CONTINUE

    def showFrameRate(self):
        self.currentTime = pg.time.get_ticks()
        delta = self.currentTime - self.lastTime
        if (delta >= 1000):
            framerate = int(1000.0 * self.numFrames/delta)
            pg.display.set_caption(f"Running at {framerate} fps.")
            self.lastTime = self.currentTime
            self.numFrames = -1
            self.frameTime = float(1000.0 / max(60,framerate))
        self.numFrames += 1

    def quit(self):
        for button in self.buttons:
            button.destroy()
        for line in self.textLines:
            line.destroy()
        self.font.destroy()

############################## top-level control ##############################
initialise_pygame()
shaders = initialise_opengl()
framebuffer = create_framebuffer()
myApp = MenuApp()
result = CONTINUE
while(result == CONTINUE):
    result = myApp.mainLoop()
    if result == NEW_GAME:
        myApp.quit()
        myApp = GameApp()
        result = CONTINUE
        continue
    if result == OPEN_MENU:
        myApp.quit()
        myApp = MenuApp()
        result = CONTINUE
        continue
myApp.quit()
teardown_program_environment(shaders, framebuffer)