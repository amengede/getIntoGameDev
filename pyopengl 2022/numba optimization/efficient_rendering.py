import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
import random
from numba import njit

def create_cubes():

    cube_positions_raw = []
    cube_eulers_raw = []
    cube_euler_velocities_raw = []
    for i in range(1000):
        cube_positions_raw.append(
            np.array(
                [random.uniform(a = -10, b = 10) for x in range(3)],
                dtype = np.float32
            )
        )
        cube_eulers_raw.append(
            np.array(
                [random.uniform(a = 0, b = 360) for x in range(3)],
                dtype = np.float32
            )
        )
        cube_euler_velocities_raw.append(
            np.array(
                [random.uniform(a = -0.1, b = 0.1) for x in range(3)],
                dtype=np.float32
            )
        )
    
    cube_positions = np.array(cube_positions_raw, dtype = np.float32)
    cube_eulers = np.array(cube_eulers_raw, dtype = np.float32)
    cube_euler_velocities = np.array(cube_euler_velocities_raw, dtype = np.float32)

    return (cube_positions, cube_eulers, cube_euler_velocities)

@njit
def update_cubes(cube_eulers, cube_euler_velocities, frame_time):

    rate = frame_time / 16.0

    for cube in range(len(cube_eulers)):

        cube_eulers[cube] = cube_eulers[cube] + rate * cube_euler_velocities[cube]

        for attribute in range(3):

            if cube_eulers[cube][attribute] < 0:
                cube_eulers[cube][attribute] += 360
            elif cube_eulers[cube][attribute] > 360:
                cube_eulers[cube][attribute] -= 360

@njit
def update_model_transforms(cube_positions, cube_eulers, model_transforms):

    for cube in range(len(cube_positions)):

        alpha = np.radians(cube_eulers[cube][0])
        beta = np.radians(cube_eulers[cube][1])
        gamma = np.radians(cube_eulers[cube][2])
        cA = np.cos(alpha)
        sA = np.sin(alpha)
        cB = np.cos(beta)
        sB = np.sin(beta)
        cG = np.cos(gamma)
        sG = np.sin(gamma)
        x = cube_positions[cube][0]
        y = cube_positions[cube][1]
        z = cube_positions[cube][2]

        model_transform = np.array(
            [
                [cB * cG, cB * sG, -sB, 0.],
                [sA * sB * cG - cA * sG, sA * sB * sG + cA * cG, sA * cB, 0.],
                [cA * sB * cG + sA * sG, cA * sB * sG - sA * cG, cA * cB, 0.],
                [x, y, z, 1.0]
            ],
            dtype = np.float32
        )
        
        model_transforms[cube] = model_transform

class App:

    def __init__(self):
        #initialise pygame
        pg.init()
        pg.display.set_mode((640,480), pg.OPENGL|pg.DOUBLEBUF)
        self.clock = pg.time.Clock()

        self.lastTime = pg.time.get_ticks()
        self.currentTime = 0
        self.numFrames = 0
        self.frameTime = 0

        (self.cube_positions, self.cube_eulers, self.cube_euler_velocities) = create_cubes()
        #initialise opengl
        glClearColor(0.1, 0.2, 0.2, 1)
        self.shader = self.createShader("shaders/vertex.txt", "shaders/fragment.txt")
        glUseProgram(self.shader)
        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)
        glEnable(GL_DEPTH_TEST)

        self.wood_texture = Material("gfx/wood.jpeg")
        self.cube_mesh = CubeMesh()

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = 640/480, 
            near = 0.1, far = 50, dtype=np.float32
        )
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader,"projection"),
            1, GL_FALSE, projection_transform
        )

        view_transform = pyrr.matrix44.create_look_at(
            eye = np.array([-10, 0, 0]),
            target = np.array([0,0,0]),
            up = np.array([0,0,1]),
            dtype = np.float32
        )
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader,"view"),
            1, GL_FALSE, view_transform
        )

        self.cube_transforms = np.array([
            pyrr.matrix44.create_identity(dtype = np.float32)

            for i in range(len(self.cube_positions))
        ], dtype=np.float32)
        self.cubeTransformVBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.cubeTransformVBO)
        glBufferData(GL_ARRAY_BUFFER, self.cube_transforms.nbytes, self.cube_transforms, GL_STATIC_DRAW)
        
        glBindVertexArray(self.cube_mesh.vao)
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 4, GL_FLOAT, GL_FALSE, 64, ctypes.c_void_p(0))
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 4, GL_FLOAT, GL_FALSE, 64, ctypes.c_void_p(16))
        glEnableVertexAttribArray(4)
        glVertexAttribPointer(4, 4, GL_FLOAT, GL_FALSE, 64, ctypes.c_void_p(32))
        glEnableVertexAttribArray(5)
        glVertexAttribPointer(5, 4, GL_FLOAT, GL_FALSE, 64, ctypes.c_void_p(48))
        #0: per shader call, 1: per instance
        glVertexAttribDivisor(2,1)
        glVertexAttribDivisor(3,1)
        glVertexAttribDivisor(4,1)
        glVertexAttribDivisor(5,1)

        self.mainLoop()

    def createShader(self, vertexFilepath, fragmentFilepath):

        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        return shader

    def mainLoop(self):
        running = True
        while (running):
            #check events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
            
            update_cubes(self.cube_eulers, self.cube_euler_velocities, self.frameTime)
            
            #refresh screen
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glUseProgram(self.shader)

            update_model_transforms(self.cube_positions, self.cube_eulers, self.cube_transforms)
            glBufferData(GL_ARRAY_BUFFER, self.cube_transforms.nbytes, self.cube_transforms, GL_STATIC_DRAW)
            
            
            self.wood_texture.use()
            glBindVertexArray(self.cube_mesh.vao)
            glDrawArraysInstanced(GL_TRIANGLES, 0, self.cube_mesh.vertex_count, len(self.cube_positions))

            pg.display.flip()

            #timing
            self.calculate_framerate()
        self.quit()

    def calculate_framerate(self):

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
        self.wood_texture.destroy()
        glDeleteProgram(self.shader)
        pg.quit()

class CubeMesh:

    def __init__(self):
        # x, y, z, s, t
        self.vertices = (
                -0.5, -0.5, -0.5, 0, 0,
                 0.5, -0.5, -0.5, 1, 0,
                 0.5,  0.5, -0.5, 1, 1,

                 0.5,  0.5, -0.5, 1, 1,
                -0.5,  0.5, -0.5, 0, 1,
                -0.5, -0.5, -0.5, 0, 0,

                -0.5, -0.5,  0.5, 0, 0,
                 0.5, -0.5,  0.5, 1, 0,
                 0.5,  0.5,  0.5, 1, 1,

                 0.5,  0.5,  0.5, 1, 1,
                -0.5,  0.5,  0.5, 0, 1,
                -0.5, -0.5,  0.5, 0, 0,

                -0.5,  0.5,  0.5, 1, 0,
                -0.5,  0.5, -0.5, 1, 1,
                -0.5, -0.5, -0.5, 0, 1,

                -0.5, -0.5, -0.5, 0, 1,
                -0.5, -0.5,  0.5, 0, 0,
                -0.5,  0.5,  0.5, 1, 0,

                 0.5,  0.5,  0.5, 1, 0,
                 0.5,  0.5, -0.5, 1, 1,
                 0.5, -0.5, -0.5, 0, 1,

                 0.5, -0.5, -0.5, 0, 1,
                 0.5, -0.5,  0.5, 0, 0,
                 0.5,  0.5,  0.5, 1, 0,

                -0.5, -0.5, -0.5, 0, 1,
                 0.5, -0.5, -0.5, 1, 1,
                 0.5, -0.5,  0.5, 1, 0,

                 0.5, -0.5,  0.5, 1, 0,
                -0.5, -0.5,  0.5, 0, 0,
                -0.5, -0.5, -0.5, 0, 1,

                -0.5,  0.5, -0.5, 0, 1,
                 0.5,  0.5, -0.5, 1, 1,
                 0.5,  0.5,  0.5, 1, 0,

                 0.5,  0.5,  0.5, 1, 0,
                -0.5,  0.5,  0.5, 0, 0,
                -0.5,  0.5, -0.5, 0, 1
            )
        self.vertex_count = len(self.vertices)//5
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))

class Material:

    
    def __init__(self, filepath):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(filepath).convert()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.texture)

    def destroy(self):
        glDeleteTextures(1, (self.texture,))

myApp = App()