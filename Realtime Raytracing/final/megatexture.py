from config import *

class MegaTexture:

    def __init__(self, filenames):
        
        texture_size = 1024
        texture_count = len(filenames)
        width = 5 * texture_size
        height = texture_count * texture_size
        """

        
        """
        textureData = pg.Surface((width,height)).convert()
        for i in range(texture_count):
            #load albedo
            image = pg.image.load(f"textures\{filenames[i]}\{filenames[i]}_albedo.png").convert()
            textureData.blit(image, (0, i * texture_size))
            #load emissive
            image = pg.image.load(f"textures\{filenames[i]}\{filenames[i]}_emissive.png").convert()
            textureData.blit(image, (texture_size, i * texture_size))
            #load glossmap
            image = pg.image.load(f"textures\{filenames[i]}\{filenames[i]}_glossiness.png").convert()
            textureData.blit(image, (2 * texture_size, i * texture_size))
            #load normal
            image = pg.image.load(f"textures\{filenames[i]}\{filenames[i]}_normal.png").convert()
            textureData.blit(image, (3 * texture_size, i * texture_size))
            #load specular
            image = pg.image.load(f"textures\{filenames[i]}\{filenames[i]}_specular.png").convert()
            textureData.blit(image, (4 * texture_size, i * texture_size))
        img_data = pg.image.tostring(textureData,"RGBA")


        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA32F,width, height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)
    
    def destroy(self):
        glDeleteTextures(1, self.texture)