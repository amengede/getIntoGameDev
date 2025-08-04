""" View: Rendering stuff """
from config import *
import model

#region constants
PIPELINE_TYPE_SKY = 0
PIPELINE_TYPE_OBJECT = 1
PIPELINE_TYPE_SKELETAL = 2

UNIFORM_TYPE_COLOR = 0
UNIFORM_TYPE_ALPHA = 1
UNIFORM_TYPE_SAMPLER_CUBE = 3
UNIFORM_TYPE_MVP = 4
UNIFORM_TYPE_FORWARDS = 5
UNIFORM_TYPE_RIGHT = 6
UNIFORM_TYPE_UP = 7
UNIFORM_TYPE_MODEL = 8
UNIFORM_TYPE_VIEWPROJ = 9
UNIFORM_TYPE_BONE_0 = 10
UNIFORM_TYPE_BONE_1 = 11
UNIFORM_TYPE_BONE_2 = 12
UNIFORM_TYPE_BONE_3 = 13
UNIFORM_TYPE_BONE_4 = 14
UNIFORM_TYPE_BONE_5 = 15
UNIFORM_TYPE_BONE_6 = 16
UNIFORM_TYPE_BONE_7 = 17
UNIFORM_TYPE_BONE_8 = 18
UNIFORM_TYPE_BONE_9 = 19
UNIFORM_TYPE_BONE_10 = 20
UNIFORM_TYPE_BONE_11 = 21
UNIFORM_TYPE_BONE_12 = 22
UNIFORM_TYPE_BONE_13 = 23
UNIFORM_TYPE_BONE_14 = 24
UNIFORM_TYPE_BONE_15 = 25
UNIFORM_TYPE_BONE_16 = 26
UNIFORM_TYPE_BONE_17 = 27
UNIFORM_TYPE_BONE_18 = 28
UNIFORM_TYPE_BONE_19 = 29
UNIFORM_TYPE_BONE_20 = 30
UNIFORM_TYPE_BONE_21 = 31
UNIFORM_TYPE_BONE_22 = 32
UNIFORM_TYPE_BONE_23 = 33
UNIFORM_TYPE_BONE_24 = 34
UNIFORM_TYPE_BONE_25 = 35
UNIFORM_TYPE_BONE_26 = 36
UNIFORM_TYPE_BONE_27 = 37
UNIFORM_TYPE_BONE_28 = 38
UNIFORM_TYPE_BONE_29 = 39
UNIFORM_TYPE_BONE_30 = 40
UNIFORM_TYPE_BONE_31 = 41
UNIFORM_TYPE_BONE_32 = 42
UNIFORM_TYPE_BONE_33 = 43
UNIFORM_TYPE_BONE_34 = 44
UNIFORM_TYPE_BONE_35 = 45
UNIFORM_TYPE_BONE_36 = 46
UNIFORM_TYPE_BONE_37 = 47
UNIFORM_TYPE_BONE_38 = 48
UNIFORM_TYPE_BONE_39 = 49

UNIFORM_NAMES = {
    PIPELINE_TYPE_OBJECT: {
        UNIFORM_TYPE_COLOR: "color",
        UNIFORM_TYPE_ALPHA: "alpha",
        UNIFORM_TYPE_MVP: "mvp",
    },

    PIPELINE_TYPE_SKY: {
        UNIFORM_TYPE_SAMPLER_CUBE: "skyBox",
        UNIFORM_TYPE_FORWARDS: "forwards",
        UNIFORM_TYPE_RIGHT: "right",
        UNIFORM_TYPE_UP: "up"
    },

    PIPELINE_TYPE_SKELETAL: {
        UNIFORM_TYPE_MODEL: "model",
        UNIFORM_TYPE_VIEWPROJ: "viewProj",
    },
}

for i in range(35):
    UNIFORM_NAMES[PIPELINE_TYPE_SKELETAL][UNIFORM_TYPE_BONE_0 + i] = f"bone_transforms[{i}]"


SHADER_FILENAMES = {
    PIPELINE_TYPE_SKY: ("shaders/vertex_3d_cubemap.txt",
                        "shaders/fragment_3d_cubemap.txt"),
    PIPELINE_TYPE_OBJECT: ("shaders/vertex_3d_colored.txt",
                            "shaders/fragment_3d_colored.txt"),
    PIPELINE_TYPE_SKELETAL: ("shaders/vertex_3d_skeletal.txt",
                            "shaders/fragment_3d_skeletal.txt"),
}

RENDERPASS_SKY = 0
RENDERPASS_WORLD = 1

DATA_TYPE_SKELETAL_VERTEX = np.dtype(
    {
        'names': [
            'pos_x',    'pos_y',    'pos_z',
            'norm_x',   'norm_y',   'norm_z',
            'tex0_x',   'tex0_y',
            'tex1_x',   'tex1_y',
            'joint_0',  'joint_1',  'joint_2',  'joint_3',
            'weight_0', 'weight_1', 'weight_2', 'weight_3'],
        'formats': [
            np.float32, np.float32, np.float32,
            np.float32, np.float32, np.float32,
            np.float32, np.float32,
            np.float32, np.float32,
            np.ubyte,   np.ubyte,   np.ubyte,   np.ubyte,
            np.float32, np.float32, np.float32, np.float32],
        'offsets': [
             0,  4,  8,
            12, 16, 20,
            24, 28,
            32, 36,
            40, 41, 42, 43,
            44, 48, 52, 56],
        'itemsize': 60
    })
#endregion
#region helper functions
def create_shader(vertex_filepath: str, fragment_filepath: str) -> int:
    """
        Compiles and links a vertex and fragment shader.

        Parameters:

            vertex_filepath (str): the vertex shader filepath

            fragment_filepath (str): the fragment shader filepath
        
        Returns:

            int: a handle to the compiled shader
    """

    with open(vertex_filepath,'r') as f:
        vertex_src = f.readlines()

    with open(fragment_filepath,'r') as f:
        fragment_src = f.readlines()

    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                            compileShader(fragment_src, GL_FRAGMENT_SHADER))

    return shader

def load_model_from_file(
    folder: str, filename: str) -> list[float]:
    """
        Load an obj model from the given filepath.

        Parameters:

            folder (str): the path to the folder

            filename (str): the name of the file in that folder
        
        Returns:

            list[float]: the model data, flattened in a list.
    """

    v = []
    vt = []
    vn = []
    vertices = []

    with open(f"{folder}/{filename}",'r') as f:
        line = f.readline()
        while line:
            words = line.split(" ")
            match words[0]:
                case "v":
                    v.append(read_attribute_data(words))
                case "vt":
                    vt.append(read_attribute_data(words))
                case "vn":
                    vn.append(read_attribute_data(words))
                case "f":
                    read_face_data(words, v, vt, vn, vertices)
            line = f.readline()

    return vertices

def read_attribute_data(words: list[str]) -> vec2 | vec3:
    """
        Read an attribute description and return its contents in a list

        Parameters:

            words (list[str]): the values to read for the attribute.
        
        Returns:

            vec2 | vec3: the parsed attributes
    """

    return [float(words[i + 1]) for i in range(len(words) - 1)]

def read_face_data(
    words: list[str], v: list[vec3],
    vt: list[vec2], vn: list[vec3],
    vertices: list[float]) -> None:
    """
        Read a face description.

        Parameters:

            words (list[str]): the corner descriptions.

            v (list[vec3]): the vertex position list

            vt (list[vec2]): the texcoord list

            vn (list[vec3]): the normal list

            vertices (list[float]): the result list

    """

    triangles_in_face = len(words) - 3

    for i in range(triangles_in_face):
        read_corner(words[1], v, vt, vn, vertices)
        read_corner(words[i + 2], v, vt, vn, vertices)
        read_corner(words[i + 3], v, vt, vn, vertices)

def read_corner(
    description: str,
    v: list[vec3], vt: list[vec2],
    vn: list[vec3], vertices: list[float]) -> None:
    """
        Read a description of a corner, adding its contents to the
        vertices.

        Parameters:

            words (list[str]): the corner descriptions.

            v (list[vec3]): the vertex position list

            vt (list[vec2]): the texcoord list

            vn (list[vec3]): the normal list

            vertices (list[float]): the result list
    """

    v_vt_vn = description.split("/")

    for x in v[int(v_vt_vn[0]) - 1]:
        vertices.append(x)
    for x in vn[int(v_vt_vn[2]) - 1]:
        vertices.append(x)

def get_element_count(attribute_type: str) -> int:
    """ Translade an attribute type into an element count """

    if attribute_type == "SCALAR":
        return 1
    elif attribute_type == "VEC2":
        return 2
    elif attribute_type == "VEC3":
        return 3
    elif attribute_type == "VEC4":
        return 4
    return 1

def get_attribute_properties(component_type: str,
                            element_count: int) -> tuple[int, bool, int]:
    """
        Translate a component type into a set of properties.
    """
    if component_type == COMPONENT_TYPE_BYTE:
        return GL_BYTE, False, element_count
    elif component_type == COMPONENT_TYPE_UNSIGNED_BYTE:
        return GL_UNSIGNED_BYTE, False, element_count
    elif component_type == COMPONENT_TYPE_SHORT:
        return GL_SHORT, False, 2 * element_count
    elif component_type == COMPONENT_TYPE_UNSIGNED_SHORT:
        return GL_UNSIGNED_SHORT, False, 2 * element_count
    elif component_type == COMPONENT_TYPE_UNSIGNED_INT:
        return GL_UNSIGNED_INT, False, 4 * element_count
    elif component_type == COMPONENT_TYPE_FLOAT:
        return GL_FLOAT, True, 4 * element_count
    return GL_BYTE, False, element_count
#endregion
class Attribute:
    """ Describes a vertex attribute """


    def __init__(self, element_count: int, element_type: int,
                normalized: int, byte_size: int, is_float: bool):

        self.element_count = element_count
        self.element_type = element_type
        self.normalized = normalized
        self.byte_size = byte_size
        self.is_float = is_float

class Mesh:
    """ A general mesh """


    def __init__(self):
        """
            Create the mesh.
        """

        self._vertex_count = 0
        self._index_count = 0
        self._index_offset = ctypes.c_void_p(0)

        self._vao = glGenVertexArrays(1)
        self._vbo = glGenBuffers(1)

    def arm_for_drawing(self) -> None:
        """
            Prepare the mesh for later drawing.
        """

        glBindVertexArray(self._vao)

    def draw(self) -> None:
        """
            Draw the mesh.
        """

        glDrawArrays(GL_TRIANGLES, 0, self._vertex_count)

    def draw_indexed(self) -> None:
        """
            Draw the mesh.
        """

        glDrawElements(GL_TRIANGLES, self._index_count,
                        GL_UNSIGNED_SHORT, self._index_offset)

    def load_from_obj(self, folderpath: str, filename: str) -> "Mesh":
        """
            Initialize the mesh, loading from the file.

            Parameters:

                folderpath: the folder to load from

                filename: the filename in the folder
        """

        vertices = np.array(
            load_model_from_file(folderpath, filename),
            dtype=np.float32
        )

        glBindVertexArray(self._vao)

        glBindBuffer(GL_ARRAY_BUFFER,self._vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        self._vertex_count = int(len(vertices)/6)

        attributes = [
            Attribute(element_count = 3, element_type = GL_FLOAT,
                        normalized = GL_FALSE, byte_size = 12,
                        is_float = True),
            Attribute(element_count = 3, element_type = GL_FLOAT,
                        normalized = GL_FALSE, byte_size = 12,
                        is_float = True)]
        self.describe(attributes)

        return self

    def load_from_gltf(self, filename: str) -> "Mesh":
        """
            Initialize the mesh, loading from the file.
        """

        attributes: list[Attribute] = []
        regions = []
        self._vertex_count = 0
        self._index_count = 0
        self._index_offset = ctypes.c_void_p(0)
        indices = np.array([], dtype=np.uint16)
        vertices = np.array([], dtype=DATA_TYPE_SKELETAL_VERTEX)

        with open(filename, "r") as file:
            data = json.load(file)
            accessor_descriptions = data["accessors"]
            buffer_views = data["bufferViews"]
            buffer_data = data["buffers"][0]["uri"]
            header, _, buffer_data = buffer_data.partition(",")
            buffer_data = base64.b64decode(buffer_data)
            attribute_description = data["meshes"][0]["primitives"][0]

            for accessor_index in attribute_description["attributes"].values():
                # get a description of the attribute
                accessor_description = accessor_descriptions[accessor_index]
                element_count = get_element_count(accessor_description["type"])
                element_type, is_float, stride = get_attribute_properties(
                    accessor_description["componentType"], element_count)
                attributes.append(Attribute(element_count, element_type,
                    GL_FALSE, stride, is_float))

                # find the attribute's region in memory
                buffer_view_index = accessor_description["bufferView"]
                buffer_view = buffer_views[buffer_view_index]
                regions.append(buffer_view)

                self._vertex_count = accessor_description["count"]

            # find the index data's region in memory
            accessor_index = attribute_description["indices"]
            accessor_description = accessor_descriptions[accessor_index]
            buffer_view_index = accessor_description["bufferView"]
            buffer_view = buffer_views[buffer_view_index]
            regions.append(buffer_view)
            self._index_offset = ctypes.c_void_p(buffer_view["byteOffset"])
            self._index_count = accessor_description["count"]

            # move interleave vertex data
            vertices = np.zeros(self._vertex_count, dtype = DATA_TYPE_SKELETAL_VERTEX)
            for i in range(self._vertex_count):
                # Position: 0
                offset = regions[0]["byteOffset"]
                stride = attributes[0].byte_size
                base_addr = offset + i * stride
                vec = get_float_3(buffer_data, base_addr)
                vertices[i]["pos_x"] = vec[0]
                vertices[i]["pos_y"] = vec[1]
                vertices[i]["pos_z"] = vec[2]
                # Normal: 1
                offset = regions[1]["byteOffset"]
                stride = attributes[1].byte_size
                base_addr = offset + i * stride
                vec = get_float_3(buffer_data, base_addr)
                vertices[i]["norm_x"] = vec[0]
                vertices[i]["norm_y"] = vec[1]
                vertices[i]["norm_z"] = vec[2]
                # Texcoord 0: 2
                offset = regions[2]["byteOffset"]
                stride = attributes[2].byte_size
                base_addr = offset + i * stride
                vec = get_float_2(buffer_data, base_addr)
                vertices[i]["tex0_x"] = vec[0]
                vertices[i]["tex0_y"] = vec[1]
                # Texcoord 1: 3
                offset = regions[3]["byteOffset"]
                stride = attributes[3].byte_size
                base_addr = offset + i * stride
                vec = get_float_2(buffer_data, base_addr)
                vertices[i]["tex1_x"] = vec[0]
                vertices[i]["tex1_y"] = vec[1]
                # Joints: 4
                offset = regions[4]["byteOffset"]
                stride = attributes[4].byte_size
                base_addr = offset + i * stride
                vec = get_unsigned_byte_4(buffer_data, base_addr)
                vertices[i]["joint_0"] = vec[0]
                vertices[i]["joint_1"] = vec[1]
                vertices[i]["joint_2"] = vec[2]
                vertices[i]["joint_3"] = vec[3]
                # Weights: 5
                offset = regions[5]["byteOffset"]
                stride = attributes[5].byte_size
                base_addr = offset + i * stride
                vec = get_float_4(buffer_data, base_addr)
                total = vec[0] + vec[1] + vec[2] + vec[3]
                vertices[i]["weight_0"] = vec[0] / total
                vertices[i]["weight_1"] = vec[1] / total
                vertices[i]["weight_2"] = vec[2] / total
                vertices[i]["weight_3"] = vec[3] / total

            # put index buffer on end
            buffer_view = regions[-1]
            offset = buffer_view["byteOffset"]
            stride = buffer_view["byteLength"]
            indices = np.zeros(self._index_count, dtype = np.uint16)
            for i in range(self._index_count):
                indices[i] = get_unsigned_short_1(buffer_data, offset + 2 * i)

        glBindVertexArray(self._vao)
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glBufferStorage(GL_ARRAY_BUFFER, vertices.nbytes + indices.nbytes, None, GL_DYNAMIC_STORAGE_BIT)
        glBufferSubData(GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)
        self.describe(attributes)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._vbo)
        glBufferSubData(GL_ELEMENT_ARRAY_BUFFER, vertices.nbytes, indices.nbytes, indices)

        return self

    def make_cuboid(self, l: float, w: float, h: float) -> "Mesh":
        """
            Create a cuboid of the given dimensions.
        """

        # x, y, z, nx, ny, nz
        vertices = (
             l/2,  w/2, -h/2,  0.0,  0.0, -1.0,
            -l/2,  w/2, -h/2,  0.0,  0.0, -1.0,
            -l/2, -w/2, -h/2,  0.0,  0.0, -1.0,

             l/2,  w/2, -h/2,  0.0,  0.0, -1.0,
             l/2, -w/2, -h/2,  0.0,  0.0, -1.0,
            -l/2, -w/2, -h/2,  0.0,  0.0, -1.0,

             l/2,  w/2,  h/2,  0.0,  0.0,  1.0,
            -l/2,  w/2,  h/2,  0.0,  0.0,  1.0,
            -l/2, -w/2,  h/2,  0.0,  0.0,  1.0,

            -l/2, -w/2,  h/2,  0.0,  0.0,  1.0,
             l/2, -w/2,  h/2,  0.0,  0.0,  1.0,
             l/2,  w/2,  h/2,  0.0,  0.0,  1.0,

            -l/2, -w/2,  h/2, -1.0,  0.0,  0.0,
            -l/2,  w/2,  h/2, -1.0,  0.0,  0.0,
            -l/2,  w/2, -h/2, -1.0,  0.0,  0.0,

            -l/2,  w/2, -h/2, -1.0,  0.0,  0.0,
            -l/2, -w/2, -h/2, -1.0,  0.0,  0.0,
            -l/2, -w/2,  h/2, -1.0,  0.0,  0.0,

             l/2, -w/2, -h/2,  1.0,  0.0,  0.0,
             l/2,  w/2, -h/2,  1.0,  0.0,  0.0,
             l/2,  w/2,  h/2,  1.0,  0.0,  0.0,

             l/2,  w/2,  h/2,  1.0,  0.0,  0.0,
             l/2, -w/2,  h/2,  1.0,  0.0,  0.0,
             l/2, -w/2, -h/2,  1.0,  0.0,  0.0,

             l/2, -w/2,  h/2,  0.0, -1.0,  0.0,
            -l/2, -w/2,  h/2,  0.0, -1.0,  0.0,
            -l/2, -w/2, -h/2,  0.0, -1.0,  0.0,

            -l/2, -w/2, -h/2,  0.0, -1.0,  0.0,
             l/2, -w/2, -h/2,  0.0, -1.0,  0.0,
             l/2, -w/2,  h/2,  0.0, -1.0,  0.0,

             l/2,  w/2, -h/2,  0.0,  1.0,  0.0,
            -l/2,  w/2, -h/2,  0.0,  1.0,  0.0,
            -l/2,  w/2,  h/2,  0.0,  1.0,  0.0,

            -l/2,  w/2,  h/2,  0.0,  1.0,  0.0,
             l/2,  w/2,  h/2,  0.0,  1.0,  0.0,
             l/2,  w/2, -h/2,  0.0,  1.0,  0.0,
        )

        self._vertex_count = int(len(vertices)/6)
        vertices = np.array(vertices, dtype=np.float32)

        glBindVertexArray(self._vao)
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glBufferData(GL_ARRAY_BUFFER,
                     vertices.nbytes, vertices, GL_STATIC_DRAW)

        attributes = [
            Attribute(element_count = 3, element_type = GL_FLOAT,
                        normalized = GL_FALSE, byte_size = 12,
                        is_float = True),
            Attribute(element_count = 3, element_type = GL_FLOAT,
                        normalized = GL_FALSE, byte_size = 12,
                        is_float = True)]
        self.describe(attributes)

        return self

    def make_quad_2d(self, center: tuple[float], size: tuple[float]) -> "Mesh":
        """ Build and upload data for a 2D Quad mesh """

        # x, y
        x,y = center
        w,h = size
        vertices = (
            x + w, y - h,
            x - w, y - h,
            x - w, y + h,

            x - w, y + h,
            x + w, y + h,
            x + w, y - h,
        )
        self._vertex_count = 6
        vertices = np.array(vertices, dtype=np.float32)

        glBindVertexArray(self._vao)
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        attributes = [
            Attribute(element_count = 2, element_type = GL_FLOAT,
                        normalized = GL_FALSE, byte_size = 8,
                        is_float = True),]
        self.describe(attributes)

        return self

    def describe(self, attributes: list[Attribute]) -> None:
        """ Build attribute pointers """

        stride = 0
        for attribute in attributes:
            stride += attribute.byte_size

        offset = 0
        for i,attribute in enumerate(attributes):
            glEnableVertexAttribArray(i)
            if attribute.is_float:
                glVertexAttribPointer(i, attribute.element_count, attribute.element_type,
                                    attribute.normalized, stride, ctypes.c_void_p(offset))
            else:
                glVertexAttribIPointer(i, attribute.element_count, attribute.element_type,
                                        stride, ctypes.c_void_p(offset))
            offset += attribute.byte_size

    def destroy(self) -> None:
        """
            Destroy the mesh, freeing any allocated memory.
        """

        glDeleteVertexArrays(1, (self._vao,))
        glDeleteBuffers(1,(self._vbo,))

class Material:
    """
        A texture of some kind.
    """


    def _start_building(self, texture_type: int, texture_unit: int):
        """
            Create the texture.

            Parameters:

                texture_type: the type of texture

                texture_unit: the texture unit
        """

        self._texture = glGenTextures(1)
        self._type = texture_type
        self._unit = texture_unit
        glBindTexture(texture_type, self._texture)

    def load_cubemap(self, filepath: str) -> "Material":
        """
            Initialize the cubemap, loading all images.

            Parameters:

                filepath: the filepath up to the texture name.
        """

        self._start_building(GL_TEXTURE_CUBE_MAP, 0)

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        #load textures
        metadata = (("_front.png", 90, GL_TEXTURE_CUBE_MAP_POSITIVE_X),
            ("_back.png", -90, GL_TEXTURE_CUBE_MAP_NEGATIVE_X),
            ("_left.png", 0, GL_TEXTURE_CUBE_MAP_NEGATIVE_Y),
            ("_right.png", 180, GL_TEXTURE_CUBE_MAP_POSITIVE_Y),
            ("_bottom.png", 0, GL_TEXTURE_CUBE_MAP_NEGATIVE_Z),
            ("_top.png", 90, GL_TEXTURE_CUBE_MAP_POSITIVE_Z))

        for (suffix, angle, target) in metadata:
            with Image.open(f"{filepath}{suffix}", mode = "r") as img:
                image_width,image_height = img.size
                img = img.rotate(angle)
                img = img.convert('RGBA')
                img_data = bytes(img.tobytes())
                glTexImage2D(target,0,GL_RGBA8,image_width,image_height,
                            0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)

        return self

    def load_tex_2d(self, filename: str) -> "Material":
        """
            Load 2D Texture data from an images
        """

        self._start_building(GL_TEXTURE_2D, 0)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        with Image.open(filename, mode = "r") as img:
            image_width,image_height = img.size
            img = img.convert('RGBA')
            img_data = bytes(img.tobytes())
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA8,image_width,image_height,
                        0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)

        return self

    def use(self) -> None:
        """
            Arm the texture for use.
        """

        glActiveTexture(GL_TEXTURE0 + self._unit)
        glBindTexture(self._type, self._texture)

    def destroy(self) -> None:
        """
            Destroy the texture, freeing memory.
        """

        glDeleteTextures(1, (self._texture,))

class Shader:
    """
        A shader.
    """


    def __init__(self, _type: int):
        """
            Initialize a new shader of the given type
        """

        vertex_filename, fragment_filename = SHADER_FILENAMES[_type]

        self._program = create_shader(vertex_filename, fragment_filename)

        self.use()
        self._locations = {}
        for uniform_type, uniform_name in UNIFORM_NAMES[_type].items():
            self._locations[uniform_type] = glGetUniformLocation(self._program, uniform_name)

    def use(self):
        """ Use the shader! """
        glUseProgram(self._program)

    def upload_integer(self, uniform_type: int, value: int):
        """
            Upload an integer.

            Parameters:

                uniform_type: the type of uniform to upload to.

                value: integer to upload
        """

        glUniform1i(self._locations[uniform_type], value)

    def upload_mat4(self, uniform_type: int, value: np.ndarray):
        """
            Upload a 4x4 matrix.

            Parameters:

                uniform_type: the type of uniform to upload to.

                value: mat4 to upload
        """

        glUniformMatrix4fv(self._locations[uniform_type], 1, GL_FALSE, value)

    def upload_mat4_list(self, uniform_type: int, values: list[np.ndarray]):
        """
            Upload a list of 4x4 matrices.

            Parameters:

                uniform_type: the type of uniform to upload to.

                value: mat4 to upload
        """

        for i,value in enumerate(values):
            glUniformMatrix4fv(self._locations[uniform_type + i], 1, GL_FALSE, value)

    def upload_vec3(self, uniform_type: int, value: np.ndarray):
        """
            Upload a 3d vector.

            Parameters:

                uniform_type: the type of uniform to upload to.

                value: vec3 to upload
        """

        glUniform3fv(self._locations[uniform_type], 1, value)

    def destroy(self) -> None:
        """ Free the memory. """
        glDeleteProgram(self._program)

class Renderpass:
    """ A renderpass """


    def __init__(self, should_clear_color: bool, should_clear_depth: bool,
                should_cull_face: bool, should_depth_test: bool):
        """
            Initialize a new renderpass
        """

        self._clear_mask = 0
        if should_clear_color:
            self._clear_mask |= GL_COLOR_BUFFER_BIT
        if should_clear_depth:
            self._clear_mask |= GL_DEPTH_BUFFER_BIT
        self.backface_cull = should_cull_face
        self.depth_test = should_depth_test

    def begin(self) -> None:
        """ Start the renderpass """
        glClear(self._clear_mask)
        if self.backface_cull:
            glEnable(GL_CULL_FACE)
        else:
            glDisable(GL_CULL_FACE)
        if self.depth_test:
            glEnable(GL_DEPTH_TEST)
        else:
            glDisable(GL_DEPTH_TEST)

class GameRenderer:
    """
        For rendering the game.
    """


    def __init__(self, window):
        """
            Create the renderer.

            Parameters:
            
                window: the glfw window to render to.
        """

        self._window = window

        self._set_up_opengl()

        self._create_assets()

        self._set_onetime_shader_data()

    def _set_up_opengl(self) -> None:
        """
            Set up OpenGL
        """

        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_CUBE_MAP_SEAMLESS)

    def _create_assets(self) -> None:
        """
            Create the meshes, materials and shaders
            used by the renderer.
        """

        self._meshes: dict[int, Mesh] = {
            OBJECT_TYPE_PLAYER: Mesh().load_from_gltf("models/Revy.gltf"),
            OBJECT_TYPE_GROUND: Mesh().load_from_obj("models", "ground.obj"),
            OBJECT_TYPE_SKY: Mesh().make_quad_2d(center = (0.0, 0.0), size = (1.0, 1.0))
        }

        self._materials: dict[int, Material] = {
            OBJECT_TYPE_SKY: Material().load_cubemap("img/sky"),
            OBJECT_TYPE_PLAYER: Material().load_tex_2d("img/Revy_Final.png")
        }

        self._colors: dict[int, np.ndarray] = {
            OBJECT_TYPE_PLAYER: np.array([0.8, 0.8, 0.8], dtype = np.float32),
            OBJECT_TYPE_GROUND: np.array([0.5, 0.5, 1.0], dtype = np.float32),
        }

        self._shaders: dict[int, Shader] = {}
        for shader_type in SHADER_FILENAMES:
            self._shaders[shader_type] = Shader(shader_type)

        self.renderpasses = {
            RENDERPASS_SKY: Renderpass(should_clear_color = True, should_clear_depth = True,
                                        should_cull_face = False, should_depth_test = False),
            RENDERPASS_WORLD: Renderpass(should_clear_color = False, should_clear_depth = False,
                                        should_cull_face = True, should_depth_test = True),
        }

    def _set_onetime_shader_data(self) -> None:
        """
            Some uniforms can be set once and forgotten.
        """

        self._projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = SCREEN_WIDTH/SCREEN_HEIGHT,
            near = 0.1, far = 150, dtype=np.float32)

        shader = self._shaders[PIPELINE_TYPE_SKY]
        shader.use()
        shader.upload_integer(UNIFORM_TYPE_SAMPLER_CUBE, 0)

    def render(self,
        camera: model.Player,
        renderables: dict[int, list[model.Entity]]) -> None:
        """
            Draw the given scene.

            Parameters:

                camera: the camera object

                renderables: set of entities to draw
        """

        self.draw_sky(camera)

        self.draw_world(camera, renderables)

        #glFlush()
        glfw.swap_buffers(self._window)

    def draw_sky(self, camera: model.Player) -> None:
        """ Draw the sky """

        right, up, forwards = camera.get_frame_of_reference()

        self.renderpasses[RENDERPASS_SKY].begin()

        shader = self._shaders[PIPELINE_TYPE_SKY]
        shader.use()
        material = self._materials[OBJECT_TYPE_SKY]
        mesh = self._meshes[OBJECT_TYPE_SKY]
        material.use()
        shader.upload_vec3(UNIFORM_TYPE_FORWARDS, forwards)
        shader.upload_vec3(UNIFORM_TYPE_RIGHT, right)
        shader.upload_vec3(UNIFORM_TYPE_UP, SCREEN_HEIGHT / SCREEN_WIDTH * up)
        mesh.arm_for_drawing()
        mesh.draw()

    def draw_world(self, camera: model.Player,
                    renderables: dict[int, list[model.Entity]]) -> None:
        """ Draw the world"""

        viewproj_transform = pyrr.matrix44.multiply(
            m1 = camera.get_view_transform(),
            m2 = self._projection_transform)

        self.renderpasses[RENDERPASS_WORLD].begin()
        shader = self._shaders[PIPELINE_TYPE_OBJECT]
        shader.use()

        # ground
        object_type = OBJECT_TYPE_GROUND
        mesh = self._meshes[object_type]
        mesh.arm_for_drawing()
        shader.upload_vec3(UNIFORM_TYPE_COLOR, self._colors[object_type])

        for _object in renderables[object_type]:

            transform_component: model.TransformComponent = _object._transform_component

            mvp_transform = pyrr.matrix44.multiply(
                m1 = transform_component.get_model_transform(),
                m2 = viewproj_transform
            )

            shader.upload_mat4(UNIFORM_TYPE_MVP, mvp_transform)
            mesh.draw()

        shader = self._shaders[PIPELINE_TYPE_SKELETAL]
        shader.use()
        shader.upload_mat4(UNIFORM_TYPE_VIEWPROJ, viewproj_transform)

        # player
        object_type = OBJECT_TYPE_PLAYER
        mesh = self._meshes[object_type]
        mesh.arm_for_drawing()
        material = self._materials[object_type]
        material.use()

        for _object in renderables[object_type]:

            #dummy_matrices = [pyrr.matrix44.create_identity(dtype=np.float32) for _ in range(40)]
            skeleton_component = _object._skeleton_component
            shader.upload_mat4_list(UNIFORM_TYPE_BONE_0, skeleton_component.get_bone_transforms())

            transform_component: model.TransformComponent = _object._transform_component

            shader.upload_mat4(UNIFORM_TYPE_MODEL, transform_component.get_model_transform())
            mesh.draw_indexed()

    def destroy(self):
        """ Free resources """

        for mesh in self._meshes.values():
            mesh.destroy()

        for material in self._materials.values():
            material.destroy()

        for shader in self._shaders.values():
            shader.destroy()
