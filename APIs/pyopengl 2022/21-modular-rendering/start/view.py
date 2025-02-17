from config import *
from view_constants import *
from shader_constants import *
import buffer
import model

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

def create_shader(vertex_filepath: str, fragment_filepath: str) -> int:
    """
        Create a shader.

        Parameters:

            vertex_filepath: filepath of the vertex source code

            fragment_filepath: filepath of the fragment source code
    """

    with open(vertex_filepath,'r') as f:
        vertex_src = f.readlines()

    with open(fragment_filepath,'r') as f:
        fragment_src = f.readlines()

    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                            compileShader(fragment_src, GL_FRAGMENT_SHADER))

    return shader


class GraphicsEngine:
    """
        Renders stuff!
    """

    def __init__(self, width: int, height: int,
                 window: "glfw.Window"):
        """
        Initialize the graphics engine.

        Parameters:

            width: width of the application window

            height: height of the application window

            window: the application window
        """

        self.width = width
        self.height = height
        self.window = window

        self.set_up_opengl()

        self.create_assets()

        self.create_framebuffers()

        self.setup_shaders()

    def set_up_opengl(self) -> None:
        """
            Set up Initial OpenGL configuration.
        """

        glClearColor(0.0, 0.0, 0.0, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_PROGRAM_POINT_SIZE)

    def create_framebuffers(self) -> None:
        """
            Create framebuffers for the program to write to.
        """

        self.fbos = []
        self.colorBuffers = []
        self.depthStencilBuffers = []
        for i in range(2):
            self.fbos.append(glGenFramebuffers(1))
            glBindFramebuffer(GL_FRAMEBUFFER, self.fbos[i])

            new_color_buffer_0 = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, new_color_buffer_0)
            glTexImage2D(
                GL_TEXTURE_2D, 0, GL_RGB,
                self.width, self.height,
                0, GL_RGB, GL_UNSIGNED_BYTE, None
            )
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glBindTexture(GL_TEXTURE_2D, 0)
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, 
                                    GL_TEXTURE_2D, new_color_buffer_0, 0)

            new_color_buffer_1 = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, new_color_buffer_1)
            glTexImage2D(
                GL_TEXTURE_2D, 0, GL_RGB, 
                self.width, self.height,
                0, GL_RGB, GL_UNSIGNED_BYTE, None
            )
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glBindTexture(GL_TEXTURE_2D, 0)
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT1, 
                                    GL_TEXTURE_2D, new_color_buffer_1, 0)

            self.colorBuffers.append([new_color_buffer_0, new_color_buffer_1])

            self.depthStencilBuffers.append(glGenRenderbuffers(1))
            glBindRenderbuffer(GL_RENDERBUFFER, self.depthStencilBuffers[i])
            glRenderbufferStorage(
                GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, self.width, self.height
            )
            glBindRenderbuffer(GL_RENDERBUFFER,0)
            glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, 
                                        GL_RENDERBUFFER, self.depthStencilBuffers[i])

            glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def setup_shaders(self) -> None:
        """
            Create and configure shaders for the program to render with.
        """

        self.shaders = {}
        self.uniform_locations = {}

        for pipeline_type in SHADERS:

            shader = create_shader(
                VERTEX_MODULE_FILENAMES[pipeline_type], 
                FRAGMENT_MODULE_FILENAMES[pipeline_type])
            glUseProgram(shader)
            self.shaders[pipeline_type] = shader

            if pipeline_type not in UNIFORM_NAMES:
                continue

            uniform_locations = {}
            for uniform_type, uniform_name in UNIFORM_NAMES[pipeline_type].items():
                uniform_locations[uniform_type] = glGetUniformLocation(shader, uniform_name)
            self.uniform_locations[pipeline_type] = uniform_locations

        # Set one-time uniforms
        projection = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = self.width/self.height,
            near = 0.1, far = 50, dtype=np.float32
        )

        pipeline_type = PIPELINE_TYPE_LIT
        shader = self.shaders[pipeline_type]
        uniform_locations = self.uniform_locations[pipeline_type]
        glUseProgram(shader)
        glUniformMatrix4fv(
            uniform_locations[UNIFORM_TYPE_PROJECTION], 1, GL_FALSE, projection)
        glUniform1i(uniform_locations[UNIFORM_TYPE_ALBEDO], 0)
        glUniform1i(uniform_locations[UNIFORM_TYPE_AMBIENT_OCCLUSION], 1)
        glUniform1i(uniform_locations[UNIFORM_TYPE_SPECULAR], 2)
        glUniform1i(uniform_locations[UNIFORM_TYPE_NORMAL], 3)
        glUniform1f(
            uniform_locations[UNIFORM_TYPE_MATERIAL_COUNT], self.advanced_material_count)

        pipeline_type = PIPELINE_TYPE_PARTICLE
        shader = self.shaders[pipeline_type]
        uniform_locations = self.uniform_locations[pipeline_type]
        glUseProgram(shader)
        glUniformMatrix4fv(
            uniform_locations[UNIFORM_TYPE_PROJECTION], 1, GL_FALSE, projection)

        pipeline_type = PIPELINE_TYPE_UNLIT
        shader = self.shaders[pipeline_type]
        uniform_locations = self.uniform_locations[pipeline_type]
        glUseProgram(shader)
        glUniformMatrix4fv(
            uniform_locations[UNIFORM_TYPE_PROJECTION], 1, GL_FALSE, projection)
        glUniform1i(uniform_locations[UNIFORM_TYPE_MATERIAL], 0)
        glUniform1f(
            uniform_locations[UNIFORM_TYPE_MATERIAL_COUNT], self.simple_material_count)

        pipeline_type = PIPELINE_TYPE_SCREEN
        shader = self.shaders[pipeline_type]
        uniform_locations = self.uniform_locations[pipeline_type]
        glUseProgram(shader)
        glUniform1i(uniform_locations[UNIFORM_TYPE_MATERIAL], 0)

        pipeline_type = PIPELINE_TYPE_BLOOM_BLUR
        shader = self.shaders[pipeline_type]
        uniform_locations = self.uniform_locations[pipeline_type]
        glUseProgram(shader)
        glUniform1i(uniform_locations[UNIFORM_TYPE_MATERIAL], 0)
        glUniform1i(uniform_locations[UNIFORM_TYPE_BRIGHT_MATERIAL], 1)

        pipeline_type = PIPELINE_TYPE_BLOOM_TRANSFER
        shader = self.shaders[pipeline_type]
        uniform_locations = self.uniform_locations[pipeline_type]
        glUseProgram(shader)
        glUniform1i(uniform_locations[UNIFORM_TYPE_MATERIAL], 0)
        glUniform1i(uniform_locations[UNIFORM_TYPE_BRIGHT_MATERIAL], 1)

        pipeline_type = PIPELINE_TYPE_BLOOM_RESOLVE
        shader = self.shaders[pipeline_type]
        uniform_locations = self.uniform_locations[pipeline_type]
        glUseProgram(shader)
        glUniform1i(uniform_locations[UNIFORM_TYPE_MATERIAL], 0)
        glUniform1i(uniform_locations[UNIFORM_TYPE_BRIGHT_MATERIAL], 1)

    def create_assets(self) -> None:
        """
            Create all the assets used for rendering.
        """

        self.create_meshes()

        self.create_materials()

    def create_meshes(self) -> None:
        """
            Load and conglomerate all meshes.
        """

        vertices = np.array([],dtype=np.float32)
        indices = np.array([], dtype=np.uint32)
        first_vertex = 0
        first_index = 0

        self.offsets = {
            FULL_ATTRIBUTES : {},
            PARTIAL_ATTRIBUTES : {}
        }

        for mesh_type, filename in FULL_ATTRIBUTE_FILENAMES.items():
            temporary_mesh = Mesh(filename)
            temporary_vertices = temporary_mesh.vertices
            vertex_count = len(temporary_vertices)//14
            temporary_indices = temporary_mesh.indices
            index_count = len(temporary_indices)
            self.offsets[FULL_ATTRIBUTES][mesh_type] = [first_vertex, first_index * 4, index_count]

            first_vertex += vertex_count
            vertices = np.append(vertices, temporary_vertices)

            first_index += index_count
            indices = np.append(indices, temporary_indices)

        for mesh_type, size in FULL_ATTRIBUTE_BILLBOARDS.items():
            temporary_mesh = BillBoard(size[0], size[1])
            temporary_vertices = temporary_mesh.vertices
            vertex_count = len(temporary_vertices)//14
            temporary_indices = temporary_mesh.indices
            index_count = len(temporary_indices)
            self.offsets[FULL_ATTRIBUTES][mesh_type] = [first_vertex, first_index * 4, index_count]

            first_vertex += vertex_count
            vertices = np.append(vertices, temporary_vertices)

            first_index += index_count
            indices = np.append(indices, temporary_indices)

        vertex_count = len(vertices)//14

        self.vaos = {}
        self.mesh_buffers = {}

        self.vaos[FULL_ATTRIBUTES] = glGenVertexArrays(1)
        glBindVertexArray(self.vaos[FULL_ATTRIBUTES])

        mesh_buffer = buffer.Buffer()
        vertex_partition = mesh_buffer.add_partition(vertices.nbytes, np.float32, GL_ARRAY_BUFFER, 0)
        index_partition = mesh_buffer.add_partition(indices.nbytes, np.uint32, GL_ELEMENT_ARRAY_BUFFER, 1)
        mesh_buffer.build()
        self.mesh_buffers[FULL_ATTRIBUTES] = mesh_buffer

        mesh_buffer.bind(vertex_partition)
        mesh_buffer.blit(vertex_partition, vertices)

        # x, y, z, s, t, nx, ny, nz, tx, ty, tz, bx, by, bz
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

        mesh_buffer.bind(index_partition)
        mesh_buffer.blit(index_partition, indices)

    def create_materials(self) -> None:
        """
            Create all the materials used by the engine.
        """

        self.simple_material_count = len(SIMPLE_MATERIAL_FILENAMES)
        self.simple_albedo_tex = load_image_layers(
                SIMPLE_MATERIAL_FILENAMES, "")

        self.advanced_material_count = len(ADVANCED_MATERIAL_FILENAMES)
        self.albedo_tex = load_image_layers(
            ADVANCED_MATERIAL_FILENAMES, "_albedo")
        self.ao_tex = load_image_layers(
            ADVANCED_MATERIAL_FILENAMES, "_ao")
        self.glossmap_tex = load_image_layers(
            ADVANCED_MATERIAL_FILENAMES, "_glossmap")
        self.normal_tex = load_image_layers(
            ADVANCED_MATERIAL_FILENAMES, "_normal")

        self.screen = TexturedQuad(0, 0, 1, 1)

        self.font = Font()
        self.fps_label = TextLine("FPS: ", self.font, (-0.9, 0.9), (0.05, 0.05))

    def update_fps(self, new_fps: int) -> None:
        """
            Rebuild the text label to reflect the given framerate.
        """

        self.fps_label.build(f"FPS: {new_fps}")

    def render_scene_objects(self, scene: model.Scene) -> None:
        """
            Render all the "3D world" objects.
        """

        view_transform = scene.player.camera.matrix
        view_position = scene.player.transform.position

        glBindFramebuffer(GL_FRAMEBUFFER, self.fbos[0])

        glDrawBuffers(2, (GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1))
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

        pipeline_type = PIPELINE_TYPE_LIT
        shader = self.shaders[pipeline_type]
        uniform_locations = self.uniform_locations[pipeline_type]
        glUseProgram(shader)

        glUniformMatrix4fv(uniform_locations[UNIFORM_TYPE_VIEW], 1, GL_FALSE, view_transform)
        glUniform3fv(uniform_locations[UNIFORM_TYPE_CAMERA_POS], 1, view_position)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self.albedo_tex)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self.ao_tex)
        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self.glossmap_tex)
        glActiveTexture(GL_TEXTURE3)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self.normal_tex)

        for i,light in enumerate(scene.lights):
            transform_component: model.TransformComponent = light.transform
            position = transform_component.position
            light_component: model.LightComponent = light.light
            color = light_component.color
            strength = light_component.strength
            glUniform3fv(uniform_locations[UNIFORM_TYPE_LIGHT0_POS + 3 * i], 1, position)
            glUniform3fv(uniform_locations[UNIFORM_TYPE_LIGHT0_COLOR + 3 * i], 1, color)
            glUniform1f(uniform_locations[UNIFORM_TYPE_LIGHT0_STRENGTH + 3 * i], strength)

        glBindVertexArray(self.vaos[FULL_ATTRIBUTES])

        for obj in scene.lit_objects:
            render_component: model.RenderComponent = obj.render
            mesh_type = render_component.mesh_type
            material_type = render_component.material_type - WOOD_MATERIAL
            transform_component: model.TransformComponent = obj.transform
            model_matrix = transform_component.matrix
            glUniform1f(
                uniform_locations[UNIFORM_TYPE_MATERIAL_INDEX], material_type)
            glUniformMatrix4fv(
                uniform_locations[UNIFORM_TYPE_MODEL], 1, GL_FALSE, model_matrix)
            base_vertex = self.offsets[FULL_ATTRIBUTES][mesh_type][0]
            mesh_buffer: buffer.Buffer = self.mesh_buffers[FULL_ATTRIBUTES]
            global_offset = mesh_buffer.partitions[1].offset
            local_offset = self.offsets[FULL_ATTRIBUTES][mesh_type][1]
            base_index = ctypes.c_void_p(local_offset + global_offset)
            index_count = self.offsets[FULL_ATTRIBUTES][mesh_type][2]

            glDrawElementsBaseVertex(GL_TRIANGLES, index_count, GL_UNSIGNED_INT, base_index, base_vertex)

        pipeline_type = PIPELINE_TYPE_UNLIT
        shader = self.shaders[pipeline_type]
        uniform_locations = self.uniform_locations[pipeline_type]
        glUseProgram(shader)

        glUniformMatrix4fv(uniform_locations[UNIFORM_TYPE_VIEW], 1, GL_FALSE, view_transform)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self.simple_albedo_tex)

        for obj in scene.unlit_objects:
            render_component: model.RenderComponent = obj.render
            mesh_type = render_component.mesh_type
            material_type = render_component.material_type - WOOD_MATERIAL
            transform_component: model.TransformComponent = obj.transform
            model_matrix = transform_component.matrix
            light_component: model.LightComponent = obj.light
            color = light_component.color

            glUniform1f(
                uniform_locations[UNIFORM_TYPE_MATERIAL_INDEX], material_type)
            glUniform3fv(
                uniform_locations[UNIFORM_TYPE_TINT], 1, color)
            glUniformMatrix4fv(
                uniform_locations[UNIFORM_TYPE_MODEL], 1, GL_FALSE, model_matrix)

            base_vertex = self.offsets[FULL_ATTRIBUTES][mesh_type][0]
            mesh_buffer: buffer.Buffer = self.mesh_buffers[FULL_ATTRIBUTES]
            global_offset = mesh_buffer.partitions[1].offset
            local_offset = self.offsets[FULL_ATTRIBUTES][mesh_type][1]
            base_index = ctypes.c_void_p(local_offset + global_offset)
            index_count = self.offsets[FULL_ATTRIBUTES][mesh_type][2]

            glDrawElementsBaseVertex(GL_TRIANGLES, index_count, GL_UNSIGNED_INT, base_index, base_vertex)

        pipeline_type = PIPELINE_TYPE_PARTICLE
        shader = self.shaders[pipeline_type]
        uniform_locations = self.uniform_locations[pipeline_type]
        glUseProgram(shader)

        glUniformMatrix4fv(uniform_locations[UNIFORM_TYPE_VIEW], 1, GL_FALSE, view_transform)

        glBindVertexArray(scene.particles.VAO)
        glDrawArrays(GL_POINTS, 0, scene.particles.particle_count)

    def render(self, scene: model.Scene) -> None:
        """
            Render the given scene.
        """

        self.render_scene_objects(scene)

        #Post processing pass
        pipeline_type = PIPELINE_TYPE_SCREEN
        shader = self.shaders[pipeline_type]
        glUseProgram(shader)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbos[0])
        glDrawBuffers(2, (GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1))
        glDisable(GL_DEPTH_TEST)

        #Bloom
        for _ in range(8):

            glBindFramebuffer(GL_FRAMEBUFFER, self.fbos[1])
            glDrawBuffers(1, (GL_COLOR_ATTACHMENT1,))
            glDisable(GL_DEPTH_TEST)

            pipeline_type = PIPELINE_TYPE_BLOOM_BLUR
            shader = self.shaders[pipeline_type]
            glUseProgram(shader)
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.colorBuffers[0][0])
            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, self.colorBuffers[0][1])
            glBindVertexArray(self.screen.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.screen.vertex_count)

            glBindFramebuffer(GL_FRAMEBUFFER, self.fbos[0])
            glDrawBuffers(1, (GL_COLOR_ATTACHMENT1,))
            glDisable(GL_DEPTH_TEST)

            pipeline_type = PIPELINE_TYPE_BLOOM_TRANSFER
            shader = self.shaders[pipeline_type]
            glUseProgram(shader)
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.colorBuffers[1][0])
            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, self.colorBuffers[1][1])
            glBindVertexArray(self.screen.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.screen.vertex_count)

        glBindFramebuffer(GL_FRAMEBUFFER, self.fbos[1])
        glDrawBuffers(1, (GL_COLOR_ATTACHMENT0,))

        pipeline_type = PIPELINE_TYPE_BLOOM_RESOLVE
        shader = self.shaders[pipeline_type]
        glUseProgram(shader)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.colorBuffers[0][0])
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.colorBuffers[0][1])
        glBindVertexArray(self.screen.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.screen.vertex_count)

        pipeline_type = PIPELINE_TYPE_SCREEN
        shader = self.shaders[pipeline_type]
        uniform_locations = self.uniform_locations[pipeline_type]
        glUseProgram(shader)
        glUniform4fv(uniform_locations[UNIFORM_TYPE_TINT], 1, np.array([1.0, 0.0, 0.0, 1.0], dtype = np.float32))
        self.font.use()
        glBindVertexArray(self.fps_label.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.fps_label.vertex_count)

        #CRT emulation pass
        pipeline_type = PIPELINE_TYPE_CRT
        shader = self.shaders[pipeline_type]
        glUseProgram(shader)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbos[0])
        glDrawBuffers(1, (GL_COLOR_ATTACHMENT0,))
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.colorBuffers[1][0])
        glBindVertexArray(self.screen.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.screen.vertex_count)

        #Put the final result on screen
        pipeline_type = PIPELINE_TYPE_SCREEN
        shader = self.shaders[pipeline_type]
        uniform_locations = self.uniform_locations[pipeline_type]
        glUseProgram(shader)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)

        glUniform4fv(uniform_locations[UNIFORM_TYPE_TINT], 1, np.array([1.0, 1.0, 1.0, 1.0], dtype = np.float32))
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.colorBuffers[0][0])
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.colorBuffers[0][1])
        glBindVertexArray(self.screen.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.screen.vertex_count)

        #For uncapped framerate: glFlush
        glfw.swap_buffers(self.window)
        #glFlush()

    def destroy(self) -> None:
        """
            Destroy everything.
        """

        glDeleteVertexArrays(1, (self.vaos[FULL_ATTRIBUTES],))
        glDeleteBuffers(1,(self.mesh_buffers[FULL_ATTRIBUTES].device_memory,))
        self.screen.destroy()
        glDeleteTextures(
            5,
            (
                self.simple_albedo_tex, self.albedo_tex, self.ao_tex,
                self.glossmap_tex, self.normal_tex
            )
        )
        self.font.destroy()
        self.fps_label.destroy()
        for shader in self.shaders.values():
            glDeleteProgram(shader)
        glDeleteTextures(len(self.colorBuffers[0]), self.colorBuffers[0])
        glDeleteTextures(len(self.colorBuffers[1]), self.colorBuffers[1])
        glDeleteRenderbuffers(len(self.depthStencilBuffers), self.depthStencilBuffers)
        glDeleteFramebuffers(len(self.fbos), self.fbos)
        glfw.destroy_window(self.window)

class Mesh:


    def __init__(self, filename: str):

        vertices, indices = self.load(filename)

        self.vertices = np.array(vertices, dtype=np.float32)
        self.indices = np.array(indices, dtype=np.uint32)

    def load(self, filename):

        #raw, unassembled data
        v = []
        vt = []
        vn = []

        #final, assembled and packed result
        vertices = []
        indices = []
        history = {}

        #open the obj file and read the data
        with open(filename,'r') as f:
            line = f.readline().replace("\n", "")
            while line:
                words = line.split(" ")
                flag = words[0]
                if flag=="v":
                    self.read_vec(v, words)
                elif flag=="vt":
                    self.read_vec(vt, words)
                elif flag=="vn":
                    self.read_vec(vn, words)
                elif flag=="f":
                    self.read_face(v, vt, vn, vertices, indices, words, history)
                line = f.readline().replace("\n", "")
        return vertices, indices

    def read_vec(self, target: list[vec], words: list[str]):
        target.append([float(x) for x in words[1:]])

    def read_face(self, 
                  v: list[list[float]], vt: list[vec], vn: list[vec], 
                  vertices: list[float], indices: list[int], words: list[str],
                  history: dict[str, int]):

        triangles_in_face = len(words) - 3

        for i in range(triangles_in_face):

            v_vt_vn_a, pos_a, tex_a, normal_a = self.unpack_corner(words[1], v, vt, vn)
            v_vt_vn_b, pos_b, tex_b, normal_b = self.unpack_corner(words[i + 2], v, vt, vn)
            v_vt_vn_c, pos_c, tex_c, normal_c = self.unpack_corner(words[i + 3], v, vt, vn)

            tangent, bitangent = self.get_btn(pos_a, tex_a, pos_b, tex_b, pos_c, tex_c)

            self.consume_corner(v_vt_vn_a, history, 
                                pos_a, tex_a, normal_a, tangent, bitangent, 
                                vertices, indices)

            self.consume_corner(v_vt_vn_b, history, 
                                pos_b, tex_b, normal_b, tangent, bitangent, 
                                vertices, indices)

            self.consume_corner(v_vt_vn_c, history, 
                                pos_c, tex_c, normal_c, tangent, bitangent, 
                                vertices, indices)

    def unpack_corner(self, v_vt_vn: str, 
                      v: list[vec], vt: list[vec], 
                      vn: list[vec]) -> tuple[str, vec, vec, vec]:

        components = [int(i) - 1 for i in v_vt_vn.split("/")]

        return v_vt_vn, v[components[0]], vt[components[1]], vn[components[2]]

    def get_btn(self, 
                pos_a: vec, tex_a: vec, 
                pos_b: vec, tex_b: vec, 
                pos_c: vec, tex_c: vec) -> tuple[vec]:

        #direction vectors
        deltaPos1 = [pos_b[i] - pos_a[i] for i in range(3)]
        deltaPos2 = [pos_c[i] - pos_a[i] for i in range(3)]
        deltaUV1 = [tex_b[i] - tex_a[i] for i in range(2)]
        deltaUV2 = [tex_c[i] - tex_a[i] for i in range(2)]
        # calculate
        den = 1 / (deltaUV1[0] * deltaUV2[1] - deltaUV2[0] * deltaUV1[1])
        tangent = []
        #tangent x
        tangent.append(den * (deltaUV2[1] * deltaPos1[0] - deltaUV1[1] * deltaPos2[0]))
        #tangent y
        tangent.append(den * (deltaUV2[1] * deltaPos1[1] - deltaUV1[1] * deltaPos2[1]))
        #tangent z
        tangent.append(den * (deltaUV2[1] * deltaPos1[2] - deltaUV1[1] * deltaPos2[2]))
        bitangent = []
        #bitangent x
        bitangent.append(den * (-deltaUV2[0] * deltaPos1[0] + deltaUV1[0] * deltaPos2[0]))
        #bitangent y
        bitangent.append(den * (-deltaUV2[0] * deltaPos1[1] + deltaUV1[0] * deltaPos2[1]))
        #bitangent z
        bitangent.append(den * (-deltaUV2[0] * deltaPos1[2] + deltaUV1[0] * deltaPos2[2]))

        return tangent, bitangent

    def consume_corner(self, v_vt_vn: str, history: dict[str, int], 
                       pos: vec, tex_coord: vec, normal: vec, 
                       tangent: vec, bitangent: vec,
                       vertices: list[float], indices: list[int]):

        if v_vt_vn in history:
            indices.append(history[v_vt_vn])
            return

        history[v_vt_vn] = len(vertices) // 14
        indices.append(history[v_vt_vn])

        for x in pos:
            vertices.append(x)
        for x in tex_coord:
            vertices.append(x)
        for x in normal:
            vertices.append(x)
        for x in tangent:
            vertices.append(x)
        for x in bitangent:
            vertices.append(x)

class Material:


    def __init__(self, filepath: str):

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        with Image.open(filepath, mode = "r") as img:
            image_width,image_height = img.size
            img = ImageOps.flip(img)
            img = img.convert('RGBA')
            img_data = bytes(img.tobytes())
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self) -> None:
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.texture)

    def destroy(self) -> None:
        glDeleteTextures(1, (self.texture,))

class BillBoard:


    def __init__(self, w: float, h: float):

        vertices = (
            0, -w/2,  h/2, 0, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0,
            0, -w/2, -h/2, 0, 1, -1, 0, 0, 0, 0, 1, 0, 1, 0,
            0,  w/2, -h/2, 1, 1, -1, 0, 0, 0, 0, 1, 0, 1, 0,
            0,  w/2,  h/2, 1, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0
        )
        self.vertices = np.array(vertices, dtype=np.float32)

        self.indices = np.array((0, 1, 2, 0, 2, 3), dtype=np.uint32)

class TexturedQuad:


    def __init__(self, x: float, y: float, w: float, h: float):
        vertices = (
            x - w, y + h, 0, 1,
            x - w, y - h, 0, 0,
            x + w, y - h, 1, 0,

            x - w, y + h, 0, 1,
            x + w, y - h, 1, 0,
            x + w, y + h, 1, 1
        )
        vertices = np.array(vertices, dtype=np.float32)

        self.vertex_count = 6

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(8))

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class Font:

    def __init__(self):

         #some parameters for fine tuning.
        w = 55.55 / 1000.0
        h = 63.88 / 1150.0
        heightOffset = -8.5 / 1150.0
        margin = 0.014

        """
            Letter: (left, top, width, height)
        """
        self.letterTexCoords = {
            'A': (       w, h,                          w - margin, margin - h), 'B': ( 3.0 * w, h,                          w - margin, margin - h),
            'C': ( 5.0 * w, h,                          w - margin, margin - h), 'D': ( 7.0 * w, h,                          w - margin, margin - h),
            'E': ( 9.0 * w, h,                          w - margin, margin - h), 'F': (11.0 * w, h,                          w - margin, margin - h),
            'G': (13.0 * w, h,                          w - margin, margin - h), 'H': (15.0 * w, h,                          w - margin, margin - h),
            'I': (17.0 * w, h,                          w - margin, margin - h), 'J': (       w, 3.0 * h + heightOffset,     w - margin, margin - h),
            'K': ( 3.0 * w, 3.0 * h + heightOffset,     w - margin, margin - h), 'L': ( 5.0 * w, 3.0 * h + heightOffset,     w - margin, margin - h),
            'M': ( 7.0 * w, 3.0 * h + heightOffset,     w - margin, margin - h), 'N': ( 9.0 * w, 3.0 * h + heightOffset,     w - margin, margin - h),
            'O': (11.0 * w, 3.0 * h + heightOffset,     w - margin, margin - h), 'P': (13.0 * w, 3.0 * h + heightOffset,     w - margin, margin - h),
            'Q': (15.0 * w, 3.0 * h + heightOffset,     w - margin, margin - h), 'R': (17.0 * w, 3.0 * h + heightOffset,     w - margin, margin - h),
            'S': (       w, 5.0 * h + 2 * heightOffset, w - margin, margin - h), 'T': ( 3.0 * w, 5.0 * h + 2 * heightOffset, w - margin, margin - h),
            'U': ( 5.0 * w, 5.0 * h + 2 * heightOffset, w - margin, margin - h), 'V': ( 7.0 * w, 5.0 * h + 2 * heightOffset, w - margin, margin - h),
            'W': ( 9.0 * w, 5.0 * h + 2 * heightOffset, w - margin, margin - h), 'X': (11.0 * w, 5.0 * h + 2 * heightOffset, w - margin, margin - h),
            'Y': (13.0 * w, 5.0 * h + 2 * heightOffset, w - margin, margin - h), 'Z': (15.0 * w, 5.0 * h + 2 * heightOffset, w - margin, margin - h),

            'a': (       w,                     7.0 * h, w - margin, margin - h), 'b': ( 3.0 * w,                     7.0 * h, w - margin, margin - h),
            'c': ( 5.0 * w,                     7.0 * h, w - margin, margin - h), 'd': ( 7.0 * w,                     7.0 * h, w - margin, margin - h),
            'e': ( 9.0 * w,                     7.0 * h, w - margin, margin - h), 'f': (11.0 * w,                     7.0 * h, w - margin, margin - h),
            'g': (13.0 * w,                     7.0 * h, w - margin, margin - h), 'h': (15.0 * w,                     7.0 * h, w - margin, margin - h),
            'i': (17.0 * w,                     7.0 * h, w - margin, margin - h), 'j': (       w,      9.0 * h + heightOffset, w - margin, margin - h),
            'k': ( 3.0 * w,      9.0 * h + heightOffset, w - margin, margin - h), 'l': ( 5.0 * w,      9.0 * h + heightOffset, w - margin, margin - h),
            'm': ( 7.0 * w,      9.0 * h + heightOffset, w - margin, margin - h), 'n': ( 9.0 * w,      9.0 * h + heightOffset, w - margin, margin - h),
            'o': (11.0 * w,      9.0 * h + heightOffset, w - margin, margin - h), 'p': (13.0 * w,      9.0 * h + heightOffset, w - margin, margin - h),
            'q': (15.0 * w,      9.0 * h + heightOffset, w - margin, margin - h), 'r': (17.0 * w,      9.0 * h + heightOffset, w - margin, margin - h),
            's': (       w, 11.0 * h + 2 * heightOffset, w - margin, margin - h), 't': ( 3.0 * w, 11.0 * h + 2 * heightOffset, w - margin, margin - h),
            'u': ( 5.0 * w, 11.0 * h + 2 * heightOffset, w - margin, margin - h), 'v': ( 7.0 * w, 11.0 * h + 2 * heightOffset, w - margin, margin - h),
            'w': ( 9.0 * w, 11.0 * h + 2 * heightOffset, w - margin, margin - h), 'x': (11.0 * w, 11.0 * h + 2 * heightOffset, w - margin, margin - h),
            'y': (13.0 * w, 11.0 * h + 2 * heightOffset, w - margin, margin - h), 'z': (15.0 * w, 11.0 * h + 2 * heightOffset, w - margin, margin - h),

            '0': (       w, 13.0 * h, w - margin, margin - h), '1':  ( 3.0 * w,                13.0 * h, w - margin, margin - h),
            '2': ( 5.0 * w, 13.0 * h, w - margin, margin - h), '3':  ( 7.0 * w,                13.0 * h, w - margin, margin - h),
            '4': ( 9.0 * w, 13.0 * h, w - margin, margin - h), '5':  (11.0 * w,                13.0 * h, w - margin, margin - h),
            '6': (13.0 * w, 13.0 * h, w - margin, margin - h), '7':  (15.0 * w,                13.0 * h, w - margin, margin - h),
            '8': (17.0 * w, 13.0 * h, w - margin, margin - h), '9':  (       w, 15.0 * h + heightOffset, w - margin, margin - h),
            
            '.':  ( 3.0 * w,     15.0 * h + heightOffset, w - margin, margin - h), ',': ( 5.0 * w,     15.0 * h + heightOffset, w - margin, margin - h),
            ';':  ( 7.0 * w,     15.0 * h + heightOffset, w - margin, margin - h), ':': ( 9.0 * w,     15.0 * h + heightOffset, w - margin, margin - h),
            '$':  (11.0 * w,     15.0 * h + heightOffset, w - margin, margin - h), '#': (13.0 * w,     15.0 * h + heightOffset, w - margin, margin - h),
            '\'': (15.0 * w,     15.0 * h + heightOffset, w - margin, margin - h), '!': (17.0 * w,     15.0 * h + heightOffset, w - margin, margin - h),
            '"':  (       w, 17.0 * h + 2 * heightOffset, w - margin, margin - h), '/': ( 3.0 * w, 17.0 * h + 2 * heightOffset, w - margin, margin - h),
            '?':  ( 5.0 * w, 17.0 * h + 2 * heightOffset, w - margin, margin - h), '%': ( 7.0 * w, 17.0 * h + 2 * heightOffset, w - margin, margin - h),
            '&':  ( 9.0 * w, 17.0 * h + 2 * heightOffset, w - margin, margin - h), '(': (11.0 * w, 17.0 * h + 2 * heightOffset, w - margin, margin - h),
            ')':  (13.0 * w, 17.0 * h + 2 * heightOffset, w - margin, margin - h), '@': (15.0 * w, 17.0 * h + 2 * heightOffset, w - margin, margin - h)
        }

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        with Image.open("img/Inconsolata.png", mode = "r") as img:
            image_width,image_height = img.size
            img = img.convert('RGBA')
            img_data = bytes(img.tobytes())
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def get_bounding_box(self, letter: str) -> tuple[float] | None:

        if letter in self.letterTexCoords:
            return self.letterTexCoords[letter]
        return None

    def use(self) -> None:
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.texture)

    def destroy(self) -> None:
        glDeleteTextures(1, (self.texture,))

class TextLine:

    def __init__(self, initial_text: str, font: Font,
                 start_position: tuple[float],
                 letter_size: tuple[float]):

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.start_position = start_position
        self.letter_size = letter_size
        self.font = font
        self.build(initial_text)

    def build(self, new_text: str) -> None:

        vertices = []
        vertex_count = 0
        write_pos = 0

        margin_adjustment = 0.96

        vertices = np.zeros(24 * len(new_text), dtype = np.float32)

        for i,letter in enumerate(new_text):

            bounding_box  = self.font.get_bounding_box(letter)
            if bounding_box is None:
                continue

            #top left
            vertices[write_pos] = self.start_position[0]\
                    - self.letter_size[0]\
                    + ((2 - margin_adjustment) * i * self.letter_size[0])
            vertices[write_pos + 1] = self.start_position[1]\
                    + self.letter_size[1]
            vertices[write_pos + 2] = bounding_box[0] - bounding_box[2]
            vertices[write_pos + 3] = bounding_box[1] + bounding_box[3]
            write_pos += 4

            #top right
            vertices[write_pos] = self.start_position[0]\
                    + self.letter_size[0]\
                    + ((2 - margin_adjustment) * i * self.letter_size[0])
            vertices[write_pos + 1] = self.start_position[1]\
                    + self.letter_size[1]
            vertices[write_pos + 2] = bounding_box[0] + bounding_box[2]
            vertices[write_pos + 3] = bounding_box[1] + bounding_box[3]
            write_pos += 4
            #bottom right
            vertices[write_pos] = self.start_position[0]\
                    + self.letter_size[0]\
                    + ((2 - margin_adjustment) * i * self.letter_size[0])
            vertices[write_pos + 1] = self.start_position[1] - self.letter_size[1]
            vertices[write_pos + 2] = bounding_box[0] + bounding_box[2]
            vertices[write_pos + 3] = bounding_box[1] - bounding_box[3]
            write_pos += 4

            #bottom right
            vertices[write_pos] = self.start_position[0]\
                    + self.letter_size[0]\
                    + ((2 - margin_adjustment) * i * self.letter_size[0])
            vertices[write_pos + 1] = self.start_position[1] - self.letter_size[1]
            vertices[write_pos + 2] = bounding_box[0] + bounding_box[2]
            vertices[write_pos + 3] = bounding_box[1] - bounding_box[3]
            write_pos += 4
            #bottom left
            vertices[write_pos] = self.start_position[0]\
                    - self.letter_size[0]\
                    + ((2 - margin_adjustment) * i * self.letter_size[0])
            vertices[write_pos + 1] = self.start_position[1]\
                    - self.letter_size[1]
            vertices[write_pos + 2] = bounding_box[0] - bounding_box[2]
            vertices[write_pos + 3] = bounding_box[1] - bounding_box[3]
            write_pos += 4
            #top left
            vertices[write_pos] = self.start_position[0]\
                    - self.letter_size[0]\
                    + ((2 - margin_adjustment) * i * self.letter_size[0])
            vertices[write_pos + 1] = self.start_position[1]\
                    + self.letter_size[1]
            vertices[write_pos + 2] = bounding_box[0] - bounding_box[2]
            vertices[write_pos + 3] = bounding_box[1] + bounding_box[3]
            write_pos += 4

            vertex_count += 6

        self.vertex_count = vertex_count
        byte_size = write_pos * 4
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, byte_size, vertices, GL_STATIC_DRAW)
        offset = 0
        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(offset))
        offset += 8
        #texture
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(offset))

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))
