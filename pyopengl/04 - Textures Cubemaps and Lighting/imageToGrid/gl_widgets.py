import ctypes
import numpy as np
import pyrr

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from PyQt6.QtCore import QSize, QRect

from PyQt6.QtGui import QSurfaceFormat, QPixmap, QImage
from PyQt6.QtOpenGL import QOpenGLVersionProfile
from PyQt6.QtOpenGLWidgets import QOpenGLWidget

import grid

class ImageFrame(QOpenGLWidget):

    def __init__(self, width, height):
        super().__init__()
        self.setFixedSize(QSize(width,height))
        self.image_loaded = False

    def initializeGL(self):

        self.fmt = QOpenGLVersionProfile()
        self.fmt.setVersion(3, 3)
        self.fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)

        self.make_assets()

        self.make_shaders()
    
    def make_assets(self):

        # Image
        # x, y, u, v
        vertices = (
            -1.0,  1.0, 0.0, 0.0,
             1.0,  1.0, 1.0, 0.0,
             1.0, -1.0, 1.0, 1.0,
            -1.0, -1.0, 0.0, 1.0
        )
        vertices = np.array(vertices, dtype=np.float32)
        
        self.image_vbo = glGenBuffers(1)
        self.image_vao = glGenVertexArrays(1)
        glBindVertexArray(self.image_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.image_vbo)

        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(8))

        # Grid Square
        # x1, y1, x2, y2
        vertices = (
            -1.0,  1.0,
             1.0,  1.0,
             1.0,  1.0,
             1.0, -1.0,
             1.0, -1.0,
            -1.0, -1.0,
            -1.0, -1.0,
            -1.0,  1.0
        )
        vertices = np.array(vertices, dtype=np.float32)
        
        self.grid_square_vbo = glGenBuffers(1)
        self.grid_square_vao = glGenVertexArrays(1)
        glBindVertexArray(self.grid_square_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.grid_square_vbo)

        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))

    def load_image(self, filename):

        self.unload_image()
        
        self.image_loaded = True

        self.image_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.image_texture)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        self.img = QPixmap(filename)
        size = self.img.size()
        self.image_length = size.width()
        self.image_width = size.height()
        self.img = self.img.toImage()
        self.img = self.img.convertedTo(QImage.Format.Format_RGBA8888)
        pixels = self.img.constBits()
        pixels.setsize(self.img.sizeInBytes())
        img_data = np.array(pixels, copy=True)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA8,self.image_length,self.image_width,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
    
    def unload_image(self):

        if not self.image_loaded:
            return
        
        self.image_loaded = False
        self.img = None
        glDeleteTextures(1, (self.image_texture,))

    def export_images(self):

        if not self.image_loaded:
            return

        for row in range(grid.grid.rows):
            for col in range(grid.grid.cols):
                box_length = self.image_length / grid.grid.cols
                box_width = self.image_width / grid.grid.rows
                x = int(col * box_length)
                y = int(row * box_width)
                cropped_image = self.img.copy(QRect(x, y, int(box_length), int(box_width)))
                cropped_image.save(f"row_{row}_col_{col}.png")
    
    def createShader(self, vertexFilepath, fragmentFilepath):

        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        return shader

    def make_shaders(self):

        self.textured_shader = self.createShader(
            "shaders/textured_vertex.txt", 
            "shaders/textured_fragment.txt"
        )

        self.untextured_shader = self.createShader(
            "shaders/untextured_vertex.txt", 
            "shaders/untextured_fragment.txt"
        )

        glUseProgram(self.untextured_shader)
        self.model_matrix_location = glGetUniformLocation(self.untextured_shader, "model")
        self.tint_location = glGetUniformLocation(self.untextured_shader, "tint")

    def paintGL(self):

        glClear(GL_COLOR_BUFFER_BIT)

        if self.image_loaded:

            # Image
            glUseProgram(self.textured_shader)
            glBindVertexArray(self.image_vao)
            glBindTexture(GL_TEXTURE_2D, self.image_texture)
            glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
        
        # Grid Squares
        glUseProgram(self.untextured_shader)
        tint = np.array([1,0,1], dtype=np.float32)
        glUniform3fv(self.tint_location, 1, tint)
        glBindVertexArray(self.grid_square_vao)

        for row in range(grid.grid.rows):
            for col in range(grid.grid.cols):
                box = grid.grid.boxes[row][col]
                model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
                model_transform = pyrr.matrix44.multiply(
                    m1 = model_transform,
                    m2 = pyrr.matrix44.create_from_scale(
                        scale = (
                            2 * grid.grid.box_length / grid.grid.image_length, 
                            2 * grid.grid.box_width / grid.grid.image_width, 
                            1
                        ), 
                        dtype = np.float32
                    )
                )
                model_transform = pyrr.matrix44.multiply(
                    m1 = model_transform,
                    m2 = pyrr.matrix44.create_from_translation(
                        vec = (
                            2 * box.x / grid.grid.image_length - 1, 
                            2 * box.y / grid.grid.image_width - 1, 
                            0
                        ), 
                        dtype = np.float32
                    )
                )
                
                glUniformMatrix4fv(self.model_matrix_location, 1, GL_FALSE, model_transform)
                glDrawArrays(GL_LINES, 0, 8)