import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr

class Component:


    def __init__(self, scale):

        self.scale = scale

class App:

    def __init__(self):
        #initialise pygame
        glfw.init()
        self.screenWidth = 640
        self.screenHeight = 480
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE)
        self.window = glfw.create_window(self.screenWidth, self.screenHeight, "Scale Transforms", None, None)
        glfw.make_context_current(self.window)

        #initialise opengl
        glClearColor(0.1, 0.2, 0.2, 1)
        self.shader = self.createShader("shaders/vertex.txt", "shaders/fragment.txt")

        self.triangle_mesh = TriangleMesh()

        glUseProgram(self.shader)

        self.triangle = Component(
            scale = [0.3,0.6,0.9]
        )

        self.triangle_mesh.build_vertices(pyrr.matrix44.create_from_scale(scale = self.triangle.scale, dtype=np.float32))

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
            if glfw.window_should_close(self.window)\
                or glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_ESCAPE) == GLFW_CONSTANTS.GLFW_PRESS:
                    running = False
            glfw.poll_events()
            
            #refresh screen
            glClear(GL_COLOR_BUFFER_BIT)
            glUseProgram(self.shader)
            
            glBindVertexArray(self.triangle_mesh.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.triangle_mesh.vertex_count)

            glfw.swap_buffers(self.window)

        self.quit()

    def quit(self):
        self.triangle_mesh.destroy()
        glDeleteProgram(self.shader)

class TriangleMesh:


    def __init__(self):

        self.originalPositions = (
            -1.0, -1.0, 0.0, 1.0,
             1.0, -1.0, 0.0, 1.0,
             0.0,  1.0, 0.0, 1.0
        )
        self.originalColors = (
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0
        )
        self.originalPositions = np.array(self.originalPositions, dtype=np.float32)
        self.originalPositions = np.reshape(
            a = self.originalPositions, 
            newshape = (3,4)
        )
        self.originalColors = np.array(self.originalColors, dtype=np.float32)
        self.originalColors = np.reshape(
            a = self.originalColors, 
            newshape = (3,3)
        )
        self.vertex_count = 3

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        self.build_vertices(pyrr.matrix44.create_identity(dtype=np.float32))

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        
    def build_vertices(self, transform):

        print(f"Original Positions:\n{self.originalPositions}")
        print(f"Transformation:\n{transform}")

        self.vertices = np.array([],dtype=np.float32)

        transformed_positions = pyrr.matrix44.multiply(
            m1 = self.originalPositions, 
            m2 = transform
        )

        print(f"After Transformation:\n{transformed_positions}")

        for i in range(self.vertex_count):

            self.vertices = np.append(self.vertices, transformed_positions[i][0:3])
            self.vertices = np.append(self.vertices, self.originalColors[i])

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

    def destroy(self):
        
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))

myApp = App()