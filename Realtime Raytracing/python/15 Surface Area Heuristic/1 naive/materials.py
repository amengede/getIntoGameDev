from config import *

class CubeMapMaterial:


    def __init__(self, filepath):

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture)

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        with Image.open(f"{filepath}_left.png", mode = "r") as img:
            image_width,image_height = img.size
            img = img.convert('RGBA')
            img_data = bytes(img.tobytes())
            glTexImage2D(
                GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,0,GL_RGBA8,image_width,image_height,
                0,GL_RGBA,GL_UNSIGNED_BYTE,img_data
            )
        
        with Image.open(f"{filepath}_right.png", mode = "r") as img:
            image_width,image_height = img.size
            img = ImageOps.flip(img)
            img = ImageOps.mirror(img)
            img = img.convert('RGBA')
            img_data = bytes(img.tobytes())
            glTexImage2D(
                GL_TEXTURE_CUBE_MAP_POSITIVE_Y,0,GL_RGBA8,image_width,image_height,
                0,GL_RGBA,GL_UNSIGNED_BYTE,img_data
            )
        
        with Image.open(f"{filepath}_top.png", mode = "r") as img:
            image_width,image_height = img.size
            img = img.rotate(90)
            img = img.convert('RGBA')
            img_data = bytes(img.tobytes())
            glTexImage2D(
                GL_TEXTURE_CUBE_MAP_POSITIVE_Z,0,GL_RGBA8,image_width,image_height,
                0,GL_RGBA,GL_UNSIGNED_BYTE,img_data
            )

        with Image.open(f"{filepath}_bottom.png", mode = "r") as img:
            image_width,image_height = img.size
            img = img.convert('RGBA')
            img_data = bytes(img.tobytes())
            glTexImage2D(
                GL_TEXTURE_CUBE_MAP_NEGATIVE_Z,0,GL_RGBA8,image_width,image_height,
                0,GL_RGBA,GL_UNSIGNED_BYTE,img_data
            )
        
        with Image.open(f"{filepath}_back.png", mode = "r") as img:
            image_width,image_height = img.size
            img = img.rotate(-90)
            img = img.convert('RGBA')
            img_data = bytes(img.tobytes())
            glTexImage2D(
                GL_TEXTURE_CUBE_MAP_NEGATIVE_X,0,GL_RGBA8,image_width,image_height,
                0,GL_RGBA,GL_UNSIGNED_BYTE,img_data
            )

        with Image.open(f"{filepath}_front.png", mode = "r") as img:
            image_width,image_height = img.size
            img = img.rotate(90)
            img = img.convert('RGBA')
            img_data = bytes(img.tobytes())
            glTexImage2D(
                GL_TEXTURE_CUBE_MAP_POSITIVE_X,0,GL_RGBA8,image_width,image_height,
                0,GL_RGBA,GL_UNSIGNED_BYTE,img_data
            )
    
    def use(self):
        glActiveTexture(GL_TEXTURE4)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture)
    
    def destroy(self):
        glDeleteTextures(1, (self.texture,))

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
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        
            glTexStorage2D(GL_TEXTURE_2D, 1, GL_RGBA16F, size, size)
            self.textures.append(newTexture)
            self.sizes.append(size)
            size *= 2
        
        self.clearColor = np.zeros(1024 * 1024 * 4, dtype = np.float16)
    
    def clear(self) -> None:

        texture = self.textures[self.detailLevel]
        size = self.sizes[self.detailLevel]

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexSubImage2D(GL_TEXTURE_2D,0,0,0,size,size,GL_RGBA,GL_HALF_FLOAT,self.clearColor)
    
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
        glBindImageTexture(0, self.textures[self.detailLevel], 0, GL_FALSE, 0, GL_READ_ONLY, GL_RGBA16F)

    def readFrom(self) -> None:

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.textures[self.detailLevel])
    
    def destroy(self) -> None:

        glDeleteTextures(len(self.textures), self.textures)