from config import *

class Material:
        
    def __init__(self, width: int, height: int):
    
        self.texture = glGenTextures(1)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, width, height, 0, GL_RGBA, GL_FLOAT, None)
    
    def writeTo(self) -> None:

        glActiveTexture(GL_TEXTURE0)
        glBindImageTexture(0, self.texture, 0, GL_FALSE, 0, GL_WRITE_ONLY, GL_RGBA32F)

    def readFrom(self) -> None:

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
    
    def destroy(self) -> None:

        glDeleteTextures(1, (self.texture,))