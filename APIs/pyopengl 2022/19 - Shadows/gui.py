from config import *
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
