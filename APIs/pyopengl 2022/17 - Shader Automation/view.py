from config import *
from view_constants import *
from shader_constants import *

class GraphicsEngine:


    def __init__(self, screenWidth, screenHeight, window):

        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.window = window

        #initialise opengl
        glClearColor(0.0, 0.0, 0.0, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.create_assets()

        self.create_framebuffers()

        self.setup_shaders()
    
    def create_framebuffers(self):
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
                self.screenWidth, self.screenHeight,
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
                self.screenWidth, self.screenHeight,
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
                GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, self.screenWidth, self.screenHeight
            )
            glBindRenderbuffer(GL_RENDERBUFFER,0)
            glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, 
                                        GL_RENDERBUFFER, self.depthStencilBuffers[i])

            glBindFramebuffer(GL_FRAMEBUFFER, 0)
    
    def setup_shaders(self):

        self.shaders = {}
        self.uniform_locations = {}

        for pipeline_type in SHADERS:

            shader = self.createShader(
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
            fovy = 45, aspect = self.screenWidth/self.screenHeight, 
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

    def create_assets(self):

        self.create_meshes()

        self.create_materials()

    def create_meshes(self):

        vertices = np.array([],dtype=np.float32)
        first_vertex = 0

        self.offsets = {
            FULL_ATTRIBUTES : {},
            PARTIAL_ATTRIBUTES : {}
        }

        for mesh_type, filename in FULL_ATTRIBUTE_FILENAMES.items():
            temporary_mesh = Mesh(filename)
            temporary_vertices = temporary_mesh.vertices
            vertex_count = len(temporary_vertices)//14
            self.offsets[FULL_ATTRIBUTES][mesh_type] = [first_vertex, vertex_count]

            first_vertex += vertex_count
            vertices = np.append(vertices, temporary_vertices)
        
        for mesh_type, size in FULL_ATTRIBUTE_BILLBOARDS.items():
            temporary_mesh = BillBoard(size[0], size[1])
            temporary_vertices = temporary_mesh.vertices
            vertex_count = len(temporary_vertices)//14
            self.offsets[FULL_ATTRIBUTES][mesh_type] = [first_vertex, vertex_count]

            first_vertex += vertex_count
            vertices = np.append(vertices, temporary_vertices)

        vertex_count = len(vertices)//14

        self.vaos = {}
        self.vbos = {}

        self.vaos[FULL_ATTRIBUTES] = glGenVertexArrays(1)
        glBindVertexArray(self.vaos[FULL_ATTRIBUTES])
        self.vbos[FULL_ATTRIBUTES] = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbos[FULL_ATTRIBUTES])
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
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

    def create_materials(self):

        self.simple_material_count = len(SIMPLE_MATERIAL_FILENAMES)
        self.simple_albedo_tex = self.load_image_layers(
            SIMPLE_MATERIAL_FILENAMES, "", self.simple_material_count
        )

        self.advanced_material_count = len(ADVANCED_MATERIAL_FILENAMES)
        self.albedo_tex = self.load_image_layers(
            ADVANCED_MATERIAL_FILENAMES, "_albedo", self.advanced_material_count
        )
        self.ao_tex = self.load_image_layers(
            ADVANCED_MATERIAL_FILENAMES, "_ao", self.advanced_material_count
        )
        self.glossmap_tex = self.load_image_layers(
            ADVANCED_MATERIAL_FILENAMES, "_glossmap", self.advanced_material_count
        )
        self.normal_tex = self.load_image_layers(
            ADVANCED_MATERIAL_FILENAMES, "_normal", self.advanced_material_count
        )

        self.screen = TexturedQuad(0, 0, 1, 1)

        self.font = Font()
        self.fps_label = TextLine("FPS: ", self.font, (-0.9, 0.9), (0.05, 0.05))
    
    def load_image_layers(self, material_collection, suffix, layer_count):

        img_data = b''

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
    
    def createShader(self, vertexFilepath, fragmentFilepath):

        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER),
                            )
        
        return shader

    def update_fps(self, new_fps):

        self.fps_label.build_text(f"FPS: {new_fps}", self.font)
    
    def render_scene_objects(self, scene):

        viewTransform = scene.player.viewTransform
        viewPosition = scene.player.position

        glBindFramebuffer(GL_FRAMEBUFFER, self.fbos[0])
        
        glDrawBuffers(2, (GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1))
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        
        pipeline_type = PIPELINE_TYPE_LIT
        shader = self.shaders[pipeline_type]
        uniform_locations = self.uniform_locations[pipeline_type]
        glUseProgram(shader)

        glUniformMatrix4fv(uniform_locations[UNIFORM_TYPE_VIEW], 1, GL_FALSE, viewTransform)
        glUniform3fv(uniform_locations[UNIFORM_TYPE_CAMERA_POS], 1, viewPosition)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self.albedo_tex)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self.ao_tex)
        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self.glossmap_tex)
        glActiveTexture(GL_TEXTURE3)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self.normal_tex)

        for i,light in enumerate(scene.lights):
            glUniform3fv(uniform_locations[UNIFORM_TYPE_LIGHT0_POS + 3 * i], 1, light.position)
            glUniform3fv(uniform_locations[UNIFORM_TYPE_LIGHT0_COLOR + 3 * i], 1, light.color)
            glUniform1f(uniform_locations[UNIFORM_TYPE_LIGHT0_STRENGTH + 3 * i], light.strength)
        
        glBindVertexArray(self.vaos[FULL_ATTRIBUTES])

        for obj in scene.lit_objects:
            glUniform1f(
                uniform_locations[UNIFORM_TYPE_MATERIAL_INDEX], obj.material_type - WOOD_MATERIAL)
            glUniformMatrix4fv(
                uniform_locations[UNIFORM_TYPE_MODEL], 1, GL_FALSE,obj.modelTransform)
            glDrawArrays(
                GL_TRIANGLES, 
                self.offsets[FULL_ATTRIBUTES][obj.mesh_type][0], 
                self.offsets[FULL_ATTRIBUTES][obj.mesh_type][1]
            )

        pipeline_type = PIPELINE_TYPE_UNLIT
        shader = self.shaders[pipeline_type]
        uniform_locations = self.uniform_locations[pipeline_type]
        glUseProgram(shader)

        glUniformMatrix4fv(uniform_locations[UNIFORM_TYPE_VIEW], 1, GL_FALSE, viewTransform)
        
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self.simple_albedo_tex)

        for obj in scene.unlit_objects:
            glUniform1f(
                uniform_locations[UNIFORM_TYPE_MATERIAL_INDEX], obj.material_type - LIGHT_MATERIAL)
            glUniform3fv(
                uniform_locations[UNIFORM_TYPE_TINT], 1, light.color)
            glUniformMatrix4fv(
                uniform_locations[UNIFORM_TYPE_MODEL], 1, GL_FALSE, obj.modelTransform)
            glDrawArrays(
                GL_TRIANGLES, 
                self.offsets[FULL_ATTRIBUTES][obj.mesh_type][0], 
                self.offsets[FULL_ATTRIBUTES][obj.mesh_type][1]
            )
    
    def render(self, scene):
        
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
        #glfw.swap_buffers(self.window)
        glFlush()

    def destroy(self):

        glDeleteVertexArrays(1, (self.vaos[FULL_ATTRIBUTES],))
        glDeleteBuffers(1,(self.vbos[FULL_ATTRIBUTES],))
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


    def __init__(self, filename):
        
        self.vertices = np.array(self.loadMesh(filename), dtype=np.float32)
    
    def loadMesh(self, filename):

        #raw, unassembled data
        v = []
        vt = []
        vn = []
        
        #final, assembled and packed result
        vertices = []

        #open the obj file and read the data
        with open(filename,'r') as f:
            line = f.readline()
            while line:
                firstSpace = line.find(" ")
                flag = line[0:firstSpace]
                if flag=="v":
                    #vertex
                    line = line.replace("v ","")
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    v.append(l)
                elif flag=="vt":
                    #texture coordinate
                    line = line.replace("vt ","")
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    vt.append(l)
                elif flag=="vn":
                    #normal
                    line = line.replace("vn ","")
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    vn.append(l)
                elif flag=="f":
                    #face, three or more vertices in v/vt/vn form
                    line = line.replace("f ","")
                    line = line.replace("\n","")
                    #get the individual vertices for each line
                    line = line.split(" ")
                    faceVertices = []
                    faceTextures = []
                    faceNormals = []
                    for vertex in line:
                        #break out into [v,vt,vn],
                        #correct for 0 based indexing.
                        l = vertex.split("/")
                        position = int(l[0]) - 1
                        faceVertices.append(v[position])
                        texture = int(l[1]) - 1
                        faceTextures.append(vt[texture])
                        normal = int(l[2]) - 1
                        faceNormals.append(vn[normal])
                    # obj file uses triangle fan format for each face individually.
                    # unpack each face
                    triangles_in_face = len(line) - 2

                    vertex_order = []
                    """
                        eg. 0,1,2,3 unpacks to vertices: [0,1,2,0,2,3]
                    """
                    for i in range(triangles_in_face):
                        vertex_order.append(0)
                        vertex_order.append(i+1)
                        vertex_order.append(i+2)
                    # calculate tangent and bitangent for point
                    # how do model positions relate to texture positions?
                    point1 = faceVertices[vertex_order[0]]
                    point2 = faceVertices[vertex_order[1]]
                    point3 = faceVertices[vertex_order[2]]
                    uv1 = faceTextures[vertex_order[0]]
                    uv2 = faceTextures[vertex_order[1]]
                    uv3 = faceTextures[vertex_order[2]]
                    #direction vectors
                    deltaPos1 = [point2[i] - point1[i] for i in range(3)]
                    deltaPos2 = [point3[i] - point1[i] for i in range(3)]
                    deltaUV1 = [uv2[i] - uv1[i] for i in range(2)]
                    deltaUV2 = [uv3[i] - uv1[i] for i in range(2)]
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
                    for i in vertex_order:
                        for x in faceVertices[i]:
                            vertices.append(x)
                        for x in faceTextures[i]:
                            vertices.append(x)
                        for x in faceNormals[i]:
                            vertices.append(x)
                        for x in tangent:
                            vertices.append(x)
                        for x in bitangent:
                            vertices.append(x)
                line = f.readline()
        return vertices

class Material:

    
    def __init__(self, filepath):

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

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.texture)

    def destroy(self):
        glDeleteTextures(1, (self.texture,))

class BillBoard:


    def __init__(self, w, h):

        self.vertices = (
            0, -w/2,  h/2, 0, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0,
            0, -w/2, -h/2, 0, 1, -1, 0, 0, 0, 0, 1, 0, 1, 0,
            0,  w/2, -h/2, 1, 1, -1, 0, 0, 0, 0, 1, 0, 1, 0,

            0, -w/2,  h/2, 0, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0,
            0,  w/2, -h/2, 1, 1, -1, 0, 0, 0, 0, 1, 0, 1, 0,
            0,  w/2,  h/2, 1, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0
        )
        self.vertices = np.array(self.vertices, dtype=np.float32)

class TexturedQuad:


    def __init__(self, x, y, w, h):
        self.vertices = (
            x - w, y + h, 0, 1,
            x - w, y - h, 0, 0,
            x + w, y - h, 1, 0,

            x - w, y + h, 0, 1,
            x + w, y - h, 1, 0,
            x + w, y + h, 1, 1
        )
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vertex_count = 6
        
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

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
        h =  63.88 / 1150.0
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
    
    def get_bounding_box(self, letter):

        if letter in self.letterTexCoords:
            return self.letterTexCoords[letter]
        return None
    
    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.texture)

    def destroy(self):
        glDeleteTextures(1, (self.texture,))

class TextLine:

    
    def __init__(self, initial_text, font, start_position, letter_size):

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.start_position = start_position
        self.letter_size = letter_size
        self.build_text(initial_text, font)
    
    def build_text(self, new_text, font):

        self.vertices = []
        self.vertex_count = 0

        margin_adjustment = 0.96

        for i,letter in enumerate(new_text):

            bounding_box  = font.get_bounding_box(letter)
            if bounding_box is None:
                continue

            #top left
            self.vertices.append(
                self.start_position[0] - self.letter_size[0] + ((2 - margin_adjustment) * i * self.letter_size[0])
            )
            self.vertices.append(self.start_position[1] + self.letter_size[1])
            self.vertices.append(bounding_box[0] - bounding_box[2])
            self.vertices.append(bounding_box[1] + bounding_box[3])
            #top right
            self.vertices.append(
                self.start_position[0] + self.letter_size[0] + ((2 - margin_adjustment) * i * self.letter_size[0])
            )
            self.vertices.append(self.start_position[1] + self.letter_size[1])
            self.vertices.append(bounding_box[0] + bounding_box[2])
            self.vertices.append(bounding_box[1] + bounding_box[3])
            #bottom right
            self.vertices.append(
                self.start_position[0] + self.letter_size[0] + ((2 - margin_adjustment) * i * self.letter_size[0])
            )
            self.vertices.append(self.start_position[1] - self.letter_size[1])
            self.vertices.append(bounding_box[0] + bounding_box[2])
            self.vertices.append(bounding_box[1] - bounding_box[3])

            #bottom right
            self.vertices.append(
                self.start_position[0] + self.letter_size[0] + ((2 - margin_adjustment) * i * self.letter_size[0])
            )
            self.vertices.append(self.start_position[1] - self.letter_size[1])
            self.vertices.append(bounding_box[0] + bounding_box[2])
            self.vertices.append(bounding_box[1] - bounding_box[3])
            #bottom left
            self.vertices.append(
                self.start_position[0] - self.letter_size[0] + ((2 - margin_adjustment) * i * self.letter_size[0])
            )
            self.vertices.append(self.start_position[1] - self.letter_size[1])
            self.vertices.append(bounding_box[0] - bounding_box[2])
            self.vertices.append(bounding_box[1] - bounding_box[3])
            #top left
            self.vertices.append(
                self.start_position[0] - self.letter_size[0] + ((2 - margin_adjustment) * i * self.letter_size[0])
            )
            self.vertices.append(self.start_position[1] + self.letter_size[1])
            self.vertices.append(bounding_box[0] - bounding_box[2])
            self.vertices.append(bounding_box[1] + bounding_box[3])

            self.vertex_count += 6

        self.vertices = np.array(self.vertices, dtype=np.float32)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
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