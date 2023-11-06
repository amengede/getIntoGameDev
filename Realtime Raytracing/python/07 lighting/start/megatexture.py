from config import *

class MegaTexture:

    def __init__(self, filenames):
        
        texture_size = 1024
        texture_count = len(filenames)
        width = 5 * texture_size
        height = texture_size

        image_types = ("albedo", "emissive", "glossiness", "normal")
        
        textureLayers = [Image.new(mode = "RGBA", size = (width, height)) for _ in range(texture_count)]
        for i in range(texture_count):
            for j, image_type in enumerate(image_types):
                with Image.open(f"textures\{filenames[i]}\{filenames[i]}_{image_type}.png", mode = "r") as img:
                    img.convert("RGBA")
                    textureLayers[i].paste(img, (j * texture_size, 0))

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self.texture)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexStorage3D(GL_TEXTURE_2D_ARRAY, 1, GL_RGBA32F,width, height,texture_count)

        for i in range(texture_count):
            img_data = bytes(textureLayers[i].tobytes())
            glTexSubImage3D(GL_TEXTURE_2D_ARRAY,0,0,0,i,width, height, 1,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
    
    def destroy(self):
        glDeleteTextures(1, self.texture)