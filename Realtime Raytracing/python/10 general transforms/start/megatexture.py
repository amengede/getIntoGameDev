from config import *

class MegaTexture:

    def __init__(self, filenames):
        
        texture_size = 1024
        texture_count = len(filenames)
        width = 5 * texture_size
        height = texture_count * texture_size

        
        textureData = Image.new(mode = "RGBA", size = (width, height))
        for i in range(texture_count):
            #load albedo
            with Image.open(f"textures\{filenames[i]}\{filenames[i]}_albedo.png", mode = "r") as img:
                img = img.convert("RGBA")
                textureData.paste(img, (0, (texture_count - i - 1) * texture_size))
            #load emissive
            with Image.open(f"textures\{filenames[i]}\{filenames[i]}_emissive.png", mode = "r") as img:
                img = img.convert("RGBA")
                textureData.paste(img, (texture_size, (texture_count - i - 1) * texture_size))
            #load glossmap
            with Image.open(f"textures\{filenames[i]}\{filenames[i]}_glossiness.png", mode = "r") as img:
                img = img.convert("RGBA")
                textureData.paste(img, (2 * texture_size, (texture_count - i - 1) * texture_size))
            #load normal
            with Image.open(f"textures\{filenames[i]}\{filenames[i]}_normal.png", mode = "r") as img:
                img = img.convert("RGBA")
                textureData.paste(img, (3 * texture_size, (texture_count - i - 1) * texture_size))
            #load specular
            with Image.open(f"textures\{filenames[i]}\{filenames[i]}_specular.png", mode = "r") as img:
                img = img.convert("RGBA")
                textureData.paste(img, (4 * texture_size, (texture_count - i - 1) * texture_size))
        img_data = bytes(textureData.tobytes())


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