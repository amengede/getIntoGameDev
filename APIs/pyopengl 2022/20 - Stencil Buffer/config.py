import pygame as pg
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
import ctypes
import random
import math

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
    pg.display.gl_set_attribute(GL_STENCIL_SIZE, 8)
    pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.OPENGL|pg.DOUBLEBUF)
    pg.mouse.set_pos((SCREEN_HEIGHT / 2, SCREEN_HEIGHT / 2))

def initialise_opengl():
    glEnable(GL_PROGRAM_POINT_SIZE)
    glClearColor(0.1, 0.1, 0.1, 1)
    shaders = []
    shader3DTextured = createShader("shaders/vertex_3d_textured.txt",
                                        "shaders/fragment_3d_textured.txt")
    shaders.append(shader3DTextured)
    shader3DColored = createShader("shaders/vertex_3d_colored.txt",
                                            "shaders/fragment_3d_colored.txt")
    shaders.append(shader3DColored)
    shader2DTextured = createShader("shaders/vertex_2d_textured.txt",
                                        "shaders/fragment_2d_textured.txt")
    shaders.append(shader2DTextured)
    shader2DColored = createShader("shaders/vertex_2d_colored.txt",
                                            "shaders/fragment_2d_colored.txt")
    shaders.append(shader2DColored)
    shader2DText = createShader("shaders/vertex_2d_textured.txt",
                                            "shaders/fragment_text.txt")
    shaders.append(shader2DText)
    shader2DParticle = createShader("shaders/particle_2d_vertex.txt",
                                            "shaders/particle_2d_fragment.txt")
    shaders.append(shader2DParticle)
    shader3DBillboard = createShader("shaders/vertex_3d_billboard.txt",
                                        "shaders/fragment_3d_billboard.txt")
    shaders.append(shader3DBillboard)
    shader3DCubemap = createShader("shaders/vertex_3d_cubemap.txt",
                                        "shaders/fragment_3d_cubemap.txt")
    shaders.append(shader3DCubemap)
    shader3DLightMap = createShader("shaders/vertex_3d_lightmap.txt",
                                        "shaders/fragment_3d_lightmap.txt")
    shaders.append(shader3DLightMap)
    shader3DOutline = createShader("shaders/vertex_3d_outline.txt",
                                        "shaders/fragment_3d_outline.txt")
    shaders.append(shader3DOutline)

    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    projection_transform = pyrr.matrix44.create_perspective_projection(45, SCREEN_WIDTH/SCREEN_HEIGHT, 
                                                                        0.1, 100, dtype=np.float32)
    
    glUseProgram(shader3DTextured)
    glUniformMatrix4fv(glGetUniformLocation(shader3DTextured,"projection"),1,GL_FALSE,projection_transform)
    glUniform3fv(glGetUniformLocation(shader3DTextured,"ambient"), 1, np.array([0.1, 0.1, 0.1],dtype=np.float32))
    glUniform3fv(glGetUniformLocation(shader3DTextured,"sun.direction"), 1, np.array([-1, 0.5, -1],dtype=np.float32))
    glUniform3fv(glGetUniformLocation(shader3DTextured,"sun.color"), 1, np.array([0.8, 0.8, 0.8],dtype=np.float32))
    glUniform1i(glGetUniformLocation(shader3DTextured, "material.diffuse"), 0)
    glUniform1i(glGetUniformLocation(shader3DTextured, "material.specular"), 1)
    glUniform1i(glGetUniformLocation(shader3DTextured, "shadowMap"), 2)

    glUseProgram(shader3DColored)
    glUniformMatrix4fv(glGetUniformLocation(shader3DColored,"projection"),1,GL_FALSE,projection_transform)

    glUseProgram(shader2DTextured)
    glUniform1i(glGetUniformLocation(shader2DTextured, "regular_texture"), 0)
    glUniform1i(glGetUniformLocation(shader2DTextured, "bright_texture"), 1)

    glUseProgram(shader3DBillboard)
    glUniformMatrix4fv(glGetUniformLocation(shader3DBillboard,"projection"),1,GL_FALSE,projection_transform)
    glUniform1i(glGetUniformLocation(shader3DBillboard, "diffuse"), 0)

    glUseProgram(shader3DCubemap)
    glUniformMatrix4fv(glGetUniformLocation(shader3DCubemap,"projection"),1,GL_FALSE,projection_transform)
    glUniform1i(glGetUniformLocation(shader3DCubemap, "skyBox"), 0)

    glUseProgram(shader3DOutline)
    glUniformMatrix4fv(glGetUniformLocation(shader3DOutline,"projection"),1,GL_FALSE,projection_transform)

    return shaders

def createShader(vertexFilepath, fragmentFilepath):

        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        return shader

def create_framebuffer():
    samples = 16
    multisampleFBO = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, multisampleFBO)
        
    regularCBMultisampled = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, regularCBMultisampled)
    glTexImage2DMultisample(GL_TEXTURE_2D_MULTISAMPLE, samples, GL_RGB, SCREEN_WIDTH, SCREEN_HEIGHT, GL_TRUE)
    glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, 0)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D_MULTISAMPLE, regularCBMultisampled, 0)

    brightCBMultisampled = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, brightCBMultisampled)
    glTexImage2DMultisample(GL_TEXTURE_2D_MULTISAMPLE, samples, GL_RGB, SCREEN_WIDTH, SCREEN_HEIGHT, GL_TRUE)
    glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, 0)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT1, GL_TEXTURE_2D_MULTISAMPLE, brightCBMultisampled, 0)
        
    MultisampleDepthStencilBuffer = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, MultisampleDepthStencilBuffer)
    glRenderbufferStorageMultisample(GL_RENDERBUFFER, samples, GL_DEPTH24_STENCIL8, SCREEN_WIDTH, SCREEN_HEIGHT)
    glBindRenderbuffer(GL_RENDERBUFFER,0)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, MultisampleDepthStencilBuffer)

    singlesampleFBO = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, singlesampleFBO)
        
    regularCB = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, regularCB)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, SCREEN_WIDTH, SCREEN_HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glBindTexture(GL_TEXTURE_2D, 0)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, 
                                GL_TEXTURE_2D, regularCB, 0)
    
    brightCB = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, brightCB)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, SCREEN_WIDTH, SCREEN_HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glBindTexture(GL_TEXTURE_2D, 0)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT1, 
                                GL_TEXTURE_2D, brightCB, 0)

    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    return (
        multisampleFBO, regularCBMultisampled, brightCBMultisampled,
        MultisampleDepthStencilBuffer, singlesampleFBO, regularCB, brightCB
        )

def teardown_program_environment(shaders, framebuffer):

    (multisampleFBO, regularCBMultisampled, brightCBMultisampled,
    MultisampleDepthStencilBuffer, singlesampleFBO, regularCB, brightCB) = framebuffer
    glDeleteTextures(4, (regularCBMultisampled, brightCBMultisampled, regularCB, brightCB))
    glDeleteRenderbuffers(1, (MultisampleDepthStencilBuffer,))
    glDeleteFramebuffers(2, (multisampleFBO, singlesampleFBO))
    
    for shader in shaders:
        glDeleteProgram(shader)
    pg.quit()

def velocity_field1(pos):
    #(-y,x) circle
    #(x,y) outwards
    return (-0.2*pos[1] + pos[0],0.2*pos[0] + pos[1])

def velocity_field2(pos):
    return (0.1,0.1)

def offset_function1():
    return (random.uniform(-0.1,0.1),random.uniform(-0.1,0.1))

def offset_function2():
    return (random.uniform(-1,1),random.uniform(-1,1))
