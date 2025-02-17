from config import *
from view_constants import *
from shader_constants import *
import buffer
import model
from shaders import *
from framebuffers import *

def load_image_layers(material_collection: dict[int, str], suffix: str) -> int:
    """
        Load a collection of materials.

        Parameters:

            material_collection: associates material types with their
                filenames.

            suffix: appended to the end of filenames. eg. "_albedo"

        Returns:

            Handle to the loaded material collection
    """

    img_data = b''

    layer_count: int = len(material_collection)

    for _, filename in material_collection.items():
        with Image.open(f"{filename}{suffix}.png", mode = "r") as img:
            img = img.convert('RGBA')
            img_data += bytes(img.tobytes())

    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D_ARRAY, tex)
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_R, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    # target, mip_level, internal_format, 
    # width, height, depth,
    # border_color, format, type, data
    glTexStorage3D(GL_TEXTURE_2D_ARRAY, 1, GL_RGBA8,
                   MATERIAL_SIZE, MATERIAL_SIZE, layer_count)

    glTexSubImage3D(GL_TEXTURE_2D_ARRAY, 0,
                    0, 0, 0,
                    MATERIAL_SIZE, MATERIAL_SIZE, layer_count,
                    GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glGenerateMipmap(GL_TEXTURE_2D_ARRAY)

    return tex

class MaterialGroup:
    """
        A collection of materials which can be bound in one
        function call.
    """

    def __init__(self):
        """
        Initialize a new MaterialGroup
        """

        self.textures: list[int] = []

    def add_texture_array(self, filenames: list[str], suffix: str) -> None:
        """
            Load and add a texture array.

            Parameters:

                filenames: set of base filenames.

                suffix: suffix to append to each of the base
                    filenames. eg. "_albedo"
        """

        self.textures.append(load_image_layers(filenames, suffix))

    def bind(self) -> None:
        """
            Bind all the textures in the group.
        """
        
        for unit, texture in enumerate(self.textures):
            glActiveTexture(GL_TEXTURE0 + unit)
            glBindTexture(GL_TEXTURE_2D_ARRAY, texture)

    def destroy(self) -> None:
        """
            Free texture resources.
        """

        glDeleteTextures(len(self.textures), self.textures)
