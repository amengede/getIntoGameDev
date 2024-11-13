############################## Imports   ######################################
#region
from config import *
#endregion
############################## Constants ######################################
#region
UNIFORM_TYPE = {
    "AMBIENT": 0,
    "VIEW": 1,
    "PROJECTION": 2,
    "CAMERA_POS": 3,
    "LIGHT_COLOR": 4,
    "LIGHT_POS": 5,
    "LIGHT_STRENGTH": 6,
    "TINT": 7,
    "LIGHT_COUNT": 8,
}
#endregion
############################## helper functions ###############################
#region
def create_shader(vertex_filepath: str, fragment_filepath: str) -> int:
    """
        Compile and link shader modules to make a shader program.

        Parameters:

            vertex_filepath: path to the text file storing the vertex
                            source code
            
            fragment_filepath: path to the text file storing the
                                fragment source code
        
        Returns:

            A handle to the created shader program
    """

    with open(vertex_filepath,'r') as f:
        vertex_src = f.readlines()

    with open(fragment_filepath,'r') as f:
        fragment_src = f.readlines()
    
    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                            compileShader(fragment_src, GL_FRAGMENT_SHADER))
    
    return shader

def load_mesh(filename: str) -> list[float]:
    """
        Load a mesh from an obj file.

        Parameters:

            filename: the filename.
        
        Returns:

            The loaded data, in a flattened format.
    """

    v = []
    vt = []
    vn = []
    vertices = []

    with open(filename, "r") as file:
        line = file.readline()

        while line:

            words = line.split(" ")
            match words[0]:
                case "v":
                    v.append(read_vertex_data(words))
                case "vt":
                    vt.append(read_texcoord_data(words))
                case "vn":
                    vn.append(read_normal_data(words))
                case "f":
                    read_face_data(words, v, vt, vn, vertices)
            line = file.readline()

    return vertices

def read_vertex_data(words: list[str]) -> list[float]:
    """
        Returns a vertex description.
    """

    return [
        float(words[1]),
        float(words[2]),
        float(words[3])
    ]

def read_texcoord_data(words: list[str]) -> list[float]:
    """
        Returns a texture coordinate description.
    """

    return [
        float(words[1]),
        float(words[2])
    ]

def read_normal_data(words: list[str]) -> list[float]:
    """
        Returns a normal vector description.
    """

    return [
        float(words[1]),
        float(words[2]),
        float(words[3])
    ]

def read_face_data(
    words: list[str], 
    v: list[list[float]], vt: list[list[float]], 
    vn: list[list[float]], vertices: list[float]) -> None:
    """
        Reads an edgetable and makes a face from it.
    """

    triangleCount = len(words) - 3

    for i in range(triangleCount):

        tangent, bitangent = get_face_orientation(words, 1, 2 + i, 3 + i, v, vt)

        make_corner(words[1], v, vt, vn, vertices, tangent, bitangent)
        make_corner(words[2 + i], v, vt, vn, vertices, tangent, bitangent)
        make_corner(words[3 + i], v, vt, vn, vertices, tangent, bitangent)

def get_face_orientation(
    words: list[str], a: int, b: int, c: int, 
    v: list[list[float]], vt: list[list[float]]) -> tuple[list[float]]:
    """
        Get the tangent and bitangent describing the given face.
    """

    v_vt_vn = words[a].split("/")
    pos1 = np.array(v[int(v_vt_vn[0]) - 1], dtype = np.float32)
    uv1 = np.array(vt[int(v_vt_vn[1]) - 1], dtype = np.float32)

    v_vt_vn = words[b].split("/")
    pos2 = np.array(v[int(v_vt_vn[0]) - 1], dtype = np.float32)
    uv2 = np.array(vt[int(v_vt_vn[1]) - 1], dtype = np.float32)

    v_vt_vn = words[c].split("/")
    pos3 = np.array(v[int(v_vt_vn[0]) - 1], dtype = np.float32)
    uv3 = np.array(vt[int(v_vt_vn[1]) - 1], dtype = np.float32)

    #direction vectors
    dPos1 = pos2 - pos1
    dPos2 = pos3 - pos1
    dUV1 = uv2 - uv1
    dUV2 = uv3 - uv1

    # calculate
    den = 1 / (dUV1[0] * dUV2[1] - dUV2[0] * dUV1[1])
    tangent = [0,0,0]
    tangent[0] = den * (dUV2[1] * dPos1[0] - dUV1[1] * dPos2[0])
    tangent[1] = den * (dUV2[1] * dPos1[1] - dUV1[1] * dPos2[1])
    tangent[2] = den * (dUV2[1] * dPos1[2] - dUV1[1] * dPos2[2])

    bitangent = [0,0,0]
    bitangent[0] = den * (-dUV2[0] * dPos1[0] + dUV1[0] * dPos2[0])
    bitangent[1] = den * (-dUV2[0] * dPos1[1] + dUV1[0] * dPos2[1])
    bitangent[2] = den * (-dUV2[0] * dPos1[2] + dUV1[0] * dPos2[2])

    return (tangent, bitangent)

def make_corner(corner_description: str, 
    v: list[list[float]], vt: list[list[float]], 
    vn: list[list[float]], vertices: list[float],
    tangent: list[float], bitangent: list[float]) -> None:
    """
        Composes a flattened description of a vertex.
    """

    v_vt_vn = corner_description.split("/")
    
    for element in v[int(v_vt_vn[0]) - 1]:
        vertices.append(element)
    for element in vt[int(v_vt_vn[1]) - 1]:
        vertices.append(element)
    for element in vn[int(v_vt_vn[2]) - 1]:
        vertices.append(element)
    for element in tangent:
        vertices.append(element)
    for element in bitangent:
        vertices.append(element)
#endregion
##################################### View ####################################
#region
class GraphicsEngine:
    """
        Draws entities and stuff.
    """
    __slots__ = (
        "meshes", "materials", "shaders", 
        "model_buffers", "light_buffer", 
        "entity_types")


    def __init__(self):
        """
            Initializes the rendering system.
        """

        self._set_up_opengl()

        self._create_assets()

        self._set_onetime_uniforms()

        self._get_uniform_locations()

    def _set_up_opengl(self) -> None:
        """
            Configure any desired OpenGL options
        """

        glClearColor(0.1, 0.1, 0.1, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
    
    def _create_assets(self) -> None:
        """
            Create all of the assets needed for drawing.
        """

        self.meshes: dict[int, Mesh] = {
            ENTITY_TYPE["CUBE"]: ObjMesh("models/cube.obj"),
            ENTITY_TYPE["POINTLIGHT"]: UntexturedCubeMesh(
                l = 0.1, w = 0.1, h = 0.1),
        }

        self.materials: dict[int, Material] = {
            ENTITY_TYPE["CUBE"]: AdvancedMaterial("crate", "png"),
        }

        self.model_buffers: dict[int, Buffer] = {
            ENTITY_TYPE["CUBE"]: Buffer(size = 1024, binding = 0),
            ENTITY_TYPE["POINTLIGHT"]: Buffer(size = 8, binding = 0)
        }

        self.light_buffer = Buffer(size = 8, binding = 1)
        
        self.shaders: dict[int, Shader] = {
            PIPELINE_TYPE["STANDARD"]: Shader(
                "shaders/vertex.txt", "shaders/fragment.txt"),
            PIPELINE_TYPE["EMISSIVE"]: Shader(
                "shaders/simple_3d_vertex.txt", 
                "shaders/simple_3d_fragment.txt"),
        }

        self.entity_types: dict[int, list[int]] = {
            PIPELINE_TYPE["STANDARD"]: [],
            PIPELINE_TYPE["EMISSIVE"]: [],
        }

    def _set_onetime_uniforms(self) -> None:
        """
            Some shader data only needs to be set once.
        """

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = 640/480, 
            near = 0.1, far = 50, dtype=np.float32
        )

        shader = self.shaders[PIPELINE_TYPE["STANDARD"]]
        shader.use()

        glUniformMatrix4fv(
            glGetUniformLocation(shader.program,"projection"),
            1, GL_FALSE, projection_transform
        )

        glUniform3fv(
            glGetUniformLocation(shader.program,"ambient"), 
            1, np.array([0.1, 0.1, 0.1],dtype=np.float32))

        glUniform1i(
            glGetUniformLocation(shader.program, "material.albedo"), 0)

        glUniform1i(
            glGetUniformLocation(shader.program, "material.ao"), 1)

        glUniform1i(
            glGetUniformLocation(shader.program, "material.normal"), 2)

        glUniform1i(
            glGetUniformLocation(shader.program, "material.specular"), 3)
        
        shader = self.shaders[PIPELINE_TYPE["EMISSIVE"]]
        shader.use()

        glUniformMatrix4fv(
            glGetUniformLocation(shader.program,"projection"),
            1, GL_FALSE, projection_transform
        )
    
    def _get_uniform_locations(self) -> None:
        """
            Query and store the locations of shader uniforms
        """

        shader = self.shaders[PIPELINE_TYPE["STANDARD"]]
        shader.use()

        shader.cache_single_location(UNIFORM_TYPE["VIEW"], "view")
        shader.cache_single_location(
            UNIFORM_TYPE["CAMERA_POS"], "cameraPos")
        shader.cache_single_location(
            UNIFORM_TYPE["LIGHT_COUNT"], "lightCount"
        )
        
        shader = self.shaders[PIPELINE_TYPE["EMISSIVE"]]
        shader.use()

        shader.cache_single_location(UNIFORM_TYPE["VIEW"], "view")
    
    def register_entity(self, pipeline_type: int, entity_type: int) -> None:
        """
            Register an entity type to be rendered with the given pipeline.
        """

        if pipeline_type not in self.entity_types:
            return

        self.entity_types[pipeline_type].append(entity_type)
    
    def render(self, 
        camera: list[np.ndarray], 
        transforms: list[np.ndarray],
        light_data: np.ndarray,
        entity_counts: np.ndarray) -> None:
        """
            Draw everything.

            Parameters:

                camera: the scene's camera

                renderables: all the entities to draw
            
        """

        self._prepare_frame(transforms, light_data)

        #refresh screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        view = camera[1]

        shader_type = PIPELINE_TYPE["STANDARD"]
        shader = self.shaders[shader_type]
        shader.use()

        glUniformMatrix4fv(
            shader.fetch_single_location(UNIFORM_TYPE["VIEW"]),
            1, GL_FALSE, view)
        glUniform3fv(
            shader.fetch_single_location(UNIFORM_TYPE["CAMERA_POS"]),
            1, camera[0])
        glUniform1i(
            shader.fetch_single_location(UNIFORM_TYPE["LIGHT_COUNT"]),
            entity_counts[ENTITY_TYPE["POINTLIGHT"]]
        )
        
        for entity_type in range(2):

            if entity_type not in self.entity_types[shader_type]:
                continue

            self.model_buffers[entity_type].read_from()
            self.materials[entity_type].use()
            self.meshes[entity_type].draw_instanced(
                0, entity_counts[entity_type])
        
        shader_type = PIPELINE_TYPE["EMISSIVE"]
        shader = self.shaders[shader_type]
        shader.use()
        
        glUniformMatrix4fv(
            shader.fetch_single_location(UNIFORM_TYPE["VIEW"]),
            1, GL_FALSE, view)

        for entity_type in range(2):

            if entity_type not in self.entity_types[shader_type]:
                continue

            self.model_buffers[entity_type].read_from()
            self.meshes[entity_type].draw_instanced(
                0, entity_counts[entity_type])

        glFlush()
    
    def _prepare_frame(self, 
        transforms: list[np.ndarray], light_data: np.ndarray) -> None:
        """
            Update model buffers based on scene data.
        """

        for entity_type, array in enumerate(transforms):

            if entity_type not in self.model_buffers:
                continue
            self.model_buffers[entity_type].consume(array)
        
        self.light_buffer.consume(light_data)
        self.light_buffer.read_from()

    def destroy(self) -> None:
        """ free any allocated memory """

        for mesh in self.meshes.values():
            mesh.destroy()
        for material in self.materials.values():
            material.destroy()
        for shader in self.shaders.values():
            shader.destroy()
        for buffer in self.model_buffers.values():
            buffer.destroy()
        self.light_buffer.destroy()

class Shader:
    """
        A shader.
    """
    __slots__ = ("program", "single_uniforms", "multi_uniforms")


    def __init__(self, vertex_filepath: str, fragment_filepath: str):
        """
            Initialize the shader.

            Parameters:

                vertex_filepath: filepath to the vertex source code.

                fragment_filepath: filepath to the fragment source code.
        """

        self.program = create_shader(vertex_filepath, fragment_filepath)

        self.single_uniforms: dict[int, int] = {}
        self.multi_uniforms: dict[int, list[int]] = {}
    
    def cache_single_location(self, 
        uniform_type: int, uniform_name: str) -> None:
        """
            Search and store the location of a uniform location.
            This is for uniforms which have one location per variable.
        """

        self.single_uniforms[uniform_type] = glGetUniformLocation(
            self.program, uniform_name)
    
    def cache_multi_location(self, 
        uniform_type: int, uniform_name: str) -> None:
        """
            Search and store the location of a uniform location.
            This is for uniforms which have multiple locations per variable.
            e.g. Arrays
        """

        if uniform_type not in self.multi_uniforms:
            self.multi_uniforms[uniform_type] = []
        
        self.multi_uniforms[uniform_type].append(
            glGetUniformLocation(
            self.program, uniform_name)
        )
    
    def fetch_single_location(self, uniform_type: int) -> int:
        """
            Returns the location of a uniform location.
            This is for uniforms which have one location per variable.
        """

        return self.single_uniforms[uniform_type]
    
    def fetch_multi_location(self, 
        uniform_type: int, index: int) -> int:
        """
            Returns the location of a uniform location.
            This is for uniforms which have multiple locations per variable.
            e.g. Arrays
        """

        return self.multi_uniforms[uniform_type][index]

    def use(self) -> None:
        """
            Use the program.
        """

        glUseProgram(self.program)
    
    def destroy(self) -> None:
        """
            Free any allocated memory.
        """

        glDeleteProgram(self.program)

class Buffer:
    """
        Storage buffer, holds arbitrary homogenous data.
    """
    __slots__ = ("binding", "device_memory", "size")


    def __init__(self, size: int, binding: int):
        """
            Initialize the buffer.

            Parameters:

                size: number of bytes on the buffer.

                binding: binding index
        """

        self.size = size
        self.binding = binding

        self.device_memory = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.device_memory)
        glBufferStorage(
            GL_SHADER_STORAGE_BUFFER, self.size, None, GL_DYNAMIC_STORAGE_BIT)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, binding, self.device_memory)
    
    def consume(self, data: np.ndarray) -> None:
        """
            Record the given element in position i, if this exceeds the buffer size,
            the buffer is resized.
        """

        incoming_size = data.nbytes

        while incoming_size > self.size:
            self.resize()

        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.device_memory)
        glBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, incoming_size, data)
    
    def resize(self) -> None:
        """
            Resize the buffer, uses doubling strategy.
        """

        self.destroy()

        self.size *= 2

        self.device_memory = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.device_memory)
        glBufferStorage(GL_SHADER_STORAGE_BUFFER, self.size, 
            None, GL_DYNAMIC_STORAGE_BIT)

    def read_from(self) -> None:
        """
            Upload the CPU data to the buffer, then arm it for reading.
        """

        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, self.binding, self.device_memory)
    
    def destroy(self) -> None:
        """
            Free the memory.
        """

        glDeleteBuffers(1, (self.device_memory,))

class Material:
    """
        A texture that can be bound and drawn.
    """
    __slots__ = ("texture", "unit", "texture_type")

    
    def __init__(self, unit: int, texture_type: int):
        """
            Initialize and the texture.

            Parameters:

                unit: the texture unit

                texture_type: the type of the texture
        """

        self.texture = glGenTextures(1)
        self.unit = unit
        self.texture_type = texture_type
        glBindTexture(texture_type, self.texture)
        glTexParameteri(texture_type, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(texture_type, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(texture_type, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(texture_type, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    def use(self) -> None:
        """
            Arm the texture for drawing.
        """

        glActiveTexture(GL_TEXTURE0 + self.unit)
        glBindTexture(self.texture_type, self.texture)

    def destroy(self) -> None:
        """
            Free the texture.
        """

        glDeleteTextures(1, (self.texture,))

class Material2D(Material):
    """
        A texture that can be bound and drawn.
    """
    __slots__ = tuple()

    
    def __init__(self, filepath: str, unit: int):
        """
            Initialize and the texture.

            Parameters:

                filepath: path to the image file.

                unit: the texture unit
        """

        super().__init__(unit, texture_type = GL_TEXTURE_2D)
        with Image.open(filepath, mode = "r") as img:
            image_width,image_height = img.size
            img = img.convert("RGBA")
            img_data = bytes(img.tobytes())
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

class AdvancedMaterial(Material):
    """
        Manages many textures.
    """
    __slots__ = ("textures")


    def __init__(self, filename: str, filetype: str):
        """
            Initialize the material, load all of its textures.

            Parameters:

                filename: the "root" filename

                filetype: the extension of the texture files
        """

        self.textures: list[Material2D] = [
            Material2D(f"img/{filename}_albedo.{filetype}", 0),
            Material2D(f"img/{filename}_ao.{filetype}", 1),
            Material2D(f"img/{filename}_normal.{filetype}", 2),
            Material2D(f"img/{filename}_specular.{filetype}", 3),
        ]

    def use(self) -> None:
        """
            Bind all the textures for drawing.
        """

        for texture in self.textures:
            texture.use()
    
    def destroy(self) -> None:
        """
            Destroy all the textures.
        """
        
        for texture in self.textures:
            texture.destroy()

class Mesh:
    """
        A basic mesh which can hold data and be drawn.
    """
    __slots__ = ("vao", "vbo", "vertex_count")


    def __init__(self):
        """
            Initialize the mesh.
        """

        # x, y, z, s, t, nx, ny, nz
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

    def arm_for_drawing(self) -> None:
        """
            Arm the triangle for drawing.
        """
        glBindVertexArray(self.vao)
    
    def draw(self) -> None:
        """
            Draw the triangle.
        """

        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def draw_instanced(self, base_instance: int, instance_count: int) -> None:
        """
            Bind and Draw the mesh as an instanced batch.
        """

        glBindVertexArray(self.vao)
        glDrawArraysInstancedBaseInstance(
            GL_TRIANGLES, 0, self.vertex_count, instance_count, base_instance)

    def destroy(self) -> None:
        """
            Free any allocated memory.
        """
        
        glDeleteVertexArrays(1,(self.vao,))
        glDeleteBuffers(1,(self.vbo,))

class UntexturedCubeMesh(Mesh):
    """
        A Mesh, hardcoded to represent a cuboid.
    """
    __slots__ = tuple()


    def __init__(self, l: float, w: float, h: float):
        """
            Build the cuboid model.
        """

        super().__init__()

        # x, y, z
        vertices = (
             l/2,  w/2, -h/2,  l/2, -w/2, -h/2, -l/2, -w/2, -h/2,  
            -l/2, -w/2, -h/2, -l/2,  w/2, -h/2,  l/2,  w/2, -h/2,

            -l/2, -w/2,  h/2,  l/2, -w/2,  h/2,  l/2,  w/2,  h/2,
             l/2,  w/2,  h/2, -l/2,  w/2,  h/2, -l/2, -w/2,  h/2,

            -l/2,  w/2,  h/2, -l/2,  w/2, -h/2, -l/2, -w/2, -h/2, 
            -l/2, -w/2, -h/2, -l/2, -w/2,  h/2, -l/2,  w/2,  h/2,

             l/2, -w/2, -h/2,  l/2,  w/2, -h/2,  l/2,  w/2,  h/2,
             l/2,  w/2,  h/2,  l/2, -w/2,  h/2,  l/2, -w/2, -h/2,

            -l/2, -w/2, -h/2,  l/2, -w/2, -h/2,  l/2, -w/2,  h/2,  
             l/2, -w/2,  h/2, -l/2, -w/2,  h/2, -l/2, -w/2, -h/2,

             l/2,  w/2,  h/2,  l/2,  w/2, -h/2, -l/2,  w/2, -h/2, 
            -l/2,  w/2, -h/2, -l/2,  w/2,  h/2,  l/2,  w/2,  h/2,
        )
        self.vertex_count = len(vertices)//3
        vertices = np.array(vertices, dtype=np.float32)

        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

class ObjMesh(Mesh):
    """
        A mesh that loads its data from an obj file.
    """
    __slots__ = tuple()


    def __init__(self, filename: str):
        """
            Load the model.
        """

        super().__init__()
        # x, y, z, s, t, nx, ny, nz, tangent, bitangent
        vertices = load_mesh(filename)
        self.vertex_count = len(vertices)//14
        vertices = np.array(vertices, dtype=np.float32)

        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        offset = 0
        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
        #texture
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 8
        #normal
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
        #tangent
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
        #bitangent
        glEnableVertexAttribArray(4)
        glVertexAttribPointer(4, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
#endregion
###############################################################################