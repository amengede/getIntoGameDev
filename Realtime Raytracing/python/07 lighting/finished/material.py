from config import *

class Material:
        
    def __init__(self, minDetail: int, maxDetail: int):

        self.detailLevel = 0
        size = minDetail
        self.textures: list[int] = []
        self.sizes: list[int] = []
        while size < maxDetail:
            newTexture = glGenTextures(1)
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, newTexture)

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        
            glTexStorage2D(GL_TEXTURE_2D, 1, GL_RGBA32F, size, size)
            self.textures.append(newTexture)
            self.sizes.append(size)
            size *= 2
    
    def upsize(self) -> None:
        """
            Attempt to increase detail level
        """
        self.detailLevel = min(len(self.textures) - 1, self.detailLevel + 1)
    
    def downsize(self) -> None:
        """
            Attempt to decrease detail level
        """
        self.detailLevel = max(0, self.detailLevel - 1)
    
    def writeTo(self) -> None:

        glActiveTexture(GL_TEXTURE0)
        glBindImageTexture(0, self.textures[self.detailLevel], 0, GL_FALSE, 0, GL_WRITE_ONLY, GL_RGBA32F)

    def readFrom(self) -> None:

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.textures[self.detailLevel])
    
    def destroy(self) -> None:

        glDeleteTextures(len(self.textures), self.textures)