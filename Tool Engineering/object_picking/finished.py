import sys

import numpy as np
from OpenGL.GL import *
import ctypes
from PyQt6.QtCore import Qt, QRect, QTimer
from PyQt6.QtGui import QSurfaceFormat, QPalette, QColor, QPaintEvent, QMouseEvent, QPainter
from PyQt6.QtOpenGL import QOpenGLBuffer, QOpenGLShader, QOpenGLShaderProgram, QOpenGLVertexArrayObject, QOpenGLVersionProfile
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QLabel, QWidget
from collections.abc import Callable
from cffi import FFI
import struct

ffi = FFI()

class Triangle:

    def __init__(self, name: str, id: int,
                pos: tuple[float], color: tuple[float]):
        self.name = name
        self.id = id
        self.pos = np.array(pos, np.float32)
        self.color = np.array(color, np.float32)

class Canvas(QWidget):
    """
        A view into the main content.
    """

    def __init__(self):
        """
            Initialize the view.

            Parameters:

                parent: The main editor program.
        """

        super().__init__()

        #self.setFixedSize(QSize(self._width, self._height))

        self.color = QColor(64, 128, 192)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
            Refreshes the view.
        """

        rect = event.rect()
        painter = QPainter(self)
        painter.fillRect(rect, self.color)

class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        self.setFixedSize(800, 600)

        self.objects = [
            Triangle("Inky", 0, (-0.4, 0.4), (1.0, 0.0, 0.0)),
            Triangle("Pinky", 1, (0.4, 0.4), (1.0, 0.0, 0.5)),
            Triangle("Blinky", 2, (-0.4, -0.4), (0.0, 1.0, 1.0)),
            Triangle("Clyde", 3, (0.4, -0.4), (0.0, 0.0, 1.0))
        ]

        widget = QWidget()
        layout = QGridLayout()
        box2 = OpenGLCanvas(self.click_callback, self.objects)
        layout.addWidget(box2, 0, 0, 12, 12)
        box3 = Canvas()
        layout.addWidget(box3, 0, 11, 12, 1)
        box1 = QLabel("Left")
        layout.addWidget(box1, 0, 0, 12, 1)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.canvas = box2
        self.inspector = box3

        self.timer = QTimer(self)
        self.timer.setInterval(17)
        self.timer.timeout.connect(self.update)
        self.timer.start()

    def update(self) -> None:

        self.canvas.repaint()

    def click_callback(self, event: QMouseEvent) -> None:
        """
            Intercepts a click and
            passes the event along to the parent to handle.
        """

        pos = event.pos()

        id = self.canvas.pick_object(pos.x(), pos.y())
        print(f"clicked on id {id}")

def make_program(parent: QOpenGLWidget,
                vertex_src: str,
                fragment_src: str) -> QOpenGLShaderProgram:

    program = QOpenGLShaderProgram(parent)
    program.addShaderFromSourceCode(QOpenGLShader.ShaderTypeBit.Vertex, vertex_src)
    program.addShaderFromSourceCode(QOpenGLShader.ShaderTypeBit.Fragment, fragment_src)
    program.link()

    return program

class VertexBuffer:

    def __init__(self):

        self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)
        self.buffer = QOpenGLBuffer()
        self.buffer.create()
        self.buffer.bind()
        self.vertex_count = 0

    def create_rgb_triangle(self) -> "VertexBuffer":

        vertPositions = np.array([
            -0.1, -0.1,
            0.1, -0.1,
            0, 0.1,], dtype=np.float32)
        glBindVertexArray(self.VAO)
        self.buffer.bind()
        self.buffer.allocate(vertPositions, vertPositions.nbytes)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        self.vertex_count = 3

        return self

    def bind(self):
        glBindVertexArray(self.VAO)

    def draw(self):
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

class Framebuffer:
    """
    Describes a collection of attachments for rendering.
    """

    def __init__(self, width: int, height: int):
        """
        Initialise a new Framebuffer.

        Parameters:

            width: requested width

            height: requested height
        """

        self.FBO = glGenFramebuffers(1)

        self.color_attachments: list[int] = []
        self.depth_stencil_attachment = None
        self.width = width
        self.height = height

        self.PBO = glGenBuffers(1)
        glBindBuffer(GL_PIXEL_PACK_BUFFER, self.PBO)
        glBufferData(GL_PIXEL_PACK_BUFFER, 4, None, GL_DYNAMIC_READ)

        self.draw_buffers = []

    def add_color_attachment(self) -> None:
        """
            Build a color attachment and add it as a render target.
        """

        glBindFramebuffer(GL_FRAMEBUFFER, self.FBO)

        attachment = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, attachment)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
            self.width, self.height,
            0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glFramebufferTexture2D(GL_FRAMEBUFFER,
                               GL_COLOR_ATTACHMENT0 + len(self.color_attachments),
                               GL_TEXTURE_2D, attachment, 0)

        self.color_attachments.append(attachment)
        self.draw_buffers.append(GL_COLOR_ATTACHMENT0)

    def add_object_id_attachment(self) -> None:
        """
            Build an object attachment and add it as a render target.
        """

        glBindFramebuffer(GL_FRAMEBUFFER, self.FBO)

        attachment = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, attachment)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_R32UI,
            self.width, self.height,
            0, GL_RED_INTEGER, GL_UNSIGNED_INT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glFramebufferTexture2D(GL_FRAMEBUFFER,
                               GL_COLOR_ATTACHMENT1,
                               GL_TEXTURE_2D, attachment, 0)

        self.color_attachments.append(attachment)
        self.draw_buffers.append(GL_COLOR_ATTACHMENT1)

    def add_depth_stencil_attachment(self) -> None:
        """
            Build and add a depth/stencil buffer.
            Every framebuffer should have at most one depth/stencil attachment
        """

        if not self.depth_stencil_attachment is None:
            glDeleteRenderbuffers(1, (self.depth_stencil_attachment,))

        glBindFramebuffer(GL_FRAMEBUFFER, self.FBO)
        self.depth_stencil_attachment = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, self.depth_stencil_attachment)
        glRenderbufferStorage(
            GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, self.width, self.height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT,
                                  GL_RENDERBUFFER, self.depth_stencil_attachment)

    def draw_to(self) -> None:

        glBindFramebuffer(GL_FRAMEBUFFER, self.FBO)
        glDrawBuffers(len(self.draw_buffers), self.draw_buffers)

    def read_from(self) -> None:

        for i,attachment in enumerate(self.color_attachments):
            glActiveTexture(GL_TEXTURE0 + i)
            glBindTexture(GL_TEXTURE_2D, attachment)

    def pick_color(self, x: int, y: int) -> tuple[int]:

        glBindFramebuffer(GL_READ_FRAMEBUFFER, self.FBO)
        glReadBuffer(GL_COLOR_ATTACHMENT0)

        glBindBuffer(GL_PIXEL_PACK_BUFFER, self.PBO)

        glReadPixels(x, self.height - y, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, 0)

        ptr = ffi.cast("char*", glMapBuffer(GL_PIXEL_PACK_BUFFER, GL_READ_ONLY))
        r = struct.unpack("<B", ptr[0])[0]
        g = struct.unpack("<B", ptr[1])[0]
        b = struct.unpack("<B", ptr[2])[0]
        glUnmapBuffer(GL_PIXEL_PACK_BUFFER)

        return (r,g,b)

    def pick_object_id(self, x: int, y: int) -> int:

        glBindFramebuffer(GL_READ_FRAMEBUFFER, self.FBO)
        glReadBuffer(GL_COLOR_ATTACHMENT1)

        glBindBuffer(GL_PIXEL_PACK_BUFFER, self.PBO)

        glReadPixels(x, self.height - y, 1, 1, GL_RED_INTEGER, GL_UNSIGNED_INT, 0)

        ptr = ffi.cast("unsigned int*", glMapBuffer(GL_PIXEL_PACK_BUFFER, GL_READ_ONLY))
        glUnmapBuffer(GL_PIXEL_PACK_BUFFER)

        return ptr[0]

    def destroy(self) -> None:

        glDeleteFramebuffers(1, (self.FBO,))
        glDeleteTextures(len(self.color_attachments), self.color_attachments)
        glDeleteBuffers(1, (self.PBO,))

class OpenGLCanvas(QOpenGLWidget):

    def __init__(self, click_callback: Callable[[QMouseEvent], None],
                objects: list[Triangle]):
        super().__init__()

        self._click_callback = click_callback
        self._objects = objects

    def initializeGL(self):

        self.tri_mesh = VertexBuffer().create_rgb_triangle()

        glClearColor(0.0, 0, 0.0, 1)

        self._framebuffer = Framebuffer(self.width(), self.height())
        self._framebuffer.add_color_attachment()
        self._framebuffer.add_object_id_attachment()

        vertShaderSrc = """
            #version 330
            layout (location=0) in vec2 pos;

            uniform vec2 translation;
            void main()
            {
                gl_Position = vec4(pos + translation, 0.0, 1.0);
            }
        """

        fragShaderSrc = """
            #version 330
            uniform vec3 color;
            uniform uint id;

            layout (location = 0) out vec4 screen_color;
            layout (location = 1) out uint object_id;
            void main()
            {
                screen_color = vec4(color, 1.0);
                object_id = id;
            }
        """

        self.program = make_program(self, vertShaderSrc, fragShaderSrc)
        self.program.bind()
        self.color_location = self.program.uniformLocation("color")
        self.translation_location = self.program.uniformLocation("translation")
        self.id_location = self.program.uniformLocation("id")

        vertShaderSrc = """
            #version 330
            
            const vec2[6] positions = vec2[6](
                vec2(-1.0, -1.0),
                vec2( 1.0, -1.0),
                vec2( 1.0,  1.0),
                vec2( 1.0,  1.0),
                vec2(-1.0,  1.0),
                vec2(-1.0, -1.0));

            out vec2 tex_coord;
            void main()
            {
                vec2 pos = positions[gl_VertexID];
                gl_Position = vec4(pos, 0.0, 1.0);
                tex_coord = 0.5 * (pos + vec2(1.0));
            }
        """

        fragShaderSrc = """
            #version 330
            in vec2 tex_coord;
            out vec4 screen_color;

            uniform sampler2D color_buffer;
            void main()
            {
                screen_color = texture(color_buffer, tex_coord);
            }
        """
        self.blit_program = make_program(self, vertShaderSrc, fragShaderSrc)

    def pick_color(self, x: int, y: int) -> tuple[int]:
        return self._framebuffer.pick_color(x, y)

    def pick_object(self, x: int, y: int) -> int:
        return self._framebuffer.pick_object_id(x, y)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self._click_callback(event)

    def resizeGL(self, w, h):
        pass

    def paintGL(self):

        self._framebuffer.draw_to()
        glViewport(0, 0, self.width(), self.height())
        glClear(GL_COLOR_BUFFER_BIT)
        self.program.bind()
        self.tri_mesh.bind()
        for _object in self._objects:
            glUniform2fv(self.translation_location, 1, _object.pos)
            glUniform3fv(self.color_location, 1, _object.color)
            glUniform1ui(self.id_location, _object.id)
            self.tri_mesh.draw()

        glBindFramebuffer(GL_FRAMEBUFFER, self.defaultFramebufferObject())
        glViewport(0, 0, 2 * self.width(), 2 * self.height())
        self._framebuffer.read_from()
        self.blit_program.bind()
        glDrawArrays(GL_TRIANGLES, 0, 6)

if __name__ == "__main__":
    format = QSurfaceFormat.defaultFormat()
    format.setMajorVersion(3)
    format.setMinorVersion(3)
    format.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    QSurfaceFormat.setDefaultFormat(format)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseDesktopOpenGL)
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec())
