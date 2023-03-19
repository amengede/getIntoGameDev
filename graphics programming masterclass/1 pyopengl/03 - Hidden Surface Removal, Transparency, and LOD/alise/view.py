from config import *
import geometry
import model

class Mesh:


    def __init__(self):

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.vertex_count = 0
    
    def destroy(self) -> None:

        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class StaticGeometry(Mesh):


    def __init__(self):

        super().__init__()
        self.vertices = np.array([], dtype = np.float32)
    
    def consume(
        self, positions: list[np.ndarray], 
        normals: list[np.ndarray], 
        model_transform: np.ndarray) -> None:
        
        vertex_count = len(positions)
        
        for i in range(vertex_count):
            self.vertices = np.append(
                self.vertices, 
                pyrr.matrix44.multiply(
                    positions[i], model_transform
                )[0:3]
            )
            self.vertices = np.append(
                self.vertices, 
                pyrr.matrix44.multiply(
                    normals[i], model_transform
                )[0:3]
            )
    
    def finalize(self):

        self.vertex_count = int(len(self.vertices) // 6)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
    
        self.vertices = None

class ObjModel(Mesh):


    def __init__(self, folderpath, filename):

        super().__init__()
        
        vertices = np.array(
            load_model_from_file(folderpath, filename),
            dtype=np.float32
        )
        self.vertex_count = int(len(vertices)/6)
        self.positions = []
        self.normals = []
        for i in range(self.vertex_count):
            self.positions.append(
                pyrr.vector4.create(
                    x = vertices[6 * i],
                    y = vertices[6 * i + 1],
                    z = vertices[6 * i + 2],
                    w = 1.0, dtype = np.float32
                )
            )

            self.normals.append(
                pyrr.vector4.create(
                    x = vertices[6 * i + 3],
                    y = vertices[6 * i + 4],
                    z = vertices[6 * i + 5],
                    w = 0.0, dtype = np.float32
                )
            )

        #vertex array object, all that stuff
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER,self.vbo)
        glBufferData(GL_ARRAY_BUFFER,vertices.nbytes,vertices,GL_STATIC_DRAW)

        #position attribute
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,vertices.itemsize*6,ctypes.c_void_p(0))
        #normal attribute
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,vertices.itemsize*6,ctypes.c_void_p(12))

class CubeMapModel(Mesh):

    
    def __init__(self, l, w, h):

        super().__init__()

        # x, y, z, nx, ny, nz
        vertices = (
            
            -l/2,  w/2, -h/2,  0,  0, -1,
             l/2,  w/2, -h/2,  0,  0, -1,
            -l/2, -w/2, -h/2,  0,  0, -1,

             l/2,  w/2, -h/2,  0,  0, -1,
             l/2, -w/2, -h/2,  0,  0, -1,
            -l/2, -w/2, -h/2,  0,  0, -1,

             l/2,  w/2,  h/2,  0,  0,  1,
            -l/2,  w/2,  h/2,  0,  0,  1,
            -l/2, -w/2,  h/2,  0,  0,  1,

            -l/2, -w/2,  h/2,  0,  0,  1,
             l/2, -w/2,  h/2,  0,  0,  1,
             l/2,  w/2,  h/2,  0,  0,  1,

            -l/2, -w/2,  h/2, -1,  0,  0,
            -l/2,  w/2,  h/2, -1,  0,  0,
            -l/2,  w/2, -h/2, -1,  0,  0,

            -l/2,  w/2, -h/2, -1,  0,  0,
            -l/2, -w/2, -h/2, -1,  0,  0,
            -l/2, -w/2,  h/2, -1,  0,  0,

             l/2, -w/2, -h/2,  1,  0,  0,
             l/2,  w/2, -h/2,  1,  0,  0,
             l/2,  w/2,  h/2,  1,  0,  0,

             l/2,  w/2,  h/2,  1,  0,  0,
             l/2, -w/2,  h/2,  1,  0,  0,
             l/2, -w/2, -h/2,  1,  0,  0,

             l/2, -w/2,  h/2,  0, -1,  0,
            -l/2, -w/2,  h/2,  0, -1,  0,
            -l/2, -w/2, -h/2,  0, -1,  0,

            -l/2, -w/2, -h/2,  0, -1,  0,
             l/2, -w/2, -h/2,  0, -1,  0,
             l/2, -w/2,  h/2,  0, -1,  0,

             l/2,  w/2, -h/2,  0,  1,  0,
            -l/2,  w/2, -h/2,  0,  1,  0,
            -l/2,  w/2,  h/2,  0,  1,  0,

            -l/2,  w/2,  h/2,  0,  1,  0,
             l/2,  w/2,  h/2,  0,  1,  0,
             l/2,  w/2, -h/2,  0,  1,  0,
        )
        self.vertex_count = len(vertices)//6
        vertices = np.array(vertices, dtype=np.float32)

        self.positions = []
        self.normals = []
        for i in range(self.vertex_count):
            self.positions.append(
                pyrr.vector4.create(
                    x = vertices[6 * i],
                    y = vertices[6 * i + 1],
                    z = vertices[6 * i + 2],
                    w = 1.0, dtype = np.float32
                )
            )

            self.normals.append(
                pyrr.vector4.create(
                    x = vertices[6 * i + 3],
                    y = vertices[6 * i + 4],
                    z = vertices[6 * i + 5],
                    w = 0.0, dtype = np.float32
                )
            )

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

class CubeMapMaterial:


    def __init__(self, filepath):

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture)

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        #load textures
        with Image.open(f"{filepath}_left.png", mode = "r") as img:
            image_width,image_height = img.size
            img = img.convert('RGBA')
            img_data = bytes(img.tobytes())
            glTexImage2D(GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,0,GL_RGBA8,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        
        with Image.open(f"{filepath}_right.png", mode = "r") as img:
            image_width,image_height = img.size
            img = ImageOps.flip(img)
            img = ImageOps.mirror(img)
            img = img.convert('RGBA')
            img_data = bytes(img.tobytes())
            glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_Y,0,GL_RGBA8,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        
        with Image.open(f"{filepath}_top.png", mode = "r") as img:
            image_width,image_height = img.size
            img = img.rotate(90)
            img = img.convert('RGBA')
            img_data = bytes(img.tobytes())
            glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_Z,0,GL_RGBA8,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)

        with Image.open(f"{filepath}_bottom.png", mode = "r") as img:
            image_width,image_height = img.size
            img = img.convert('RGBA')
            img_data = bytes(img.tobytes())
            glTexImage2D(GL_TEXTURE_CUBE_MAP_NEGATIVE_Z,0,GL_RGBA8,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        
        with Image.open(f"{filepath}_back.png", mode = "r") as img:
            image_width,image_height = img.size
            img = img.rotate(-90)
            img = img.convert('RGBA')
            img_data = bytes(img.tobytes())
            glTexImage2D(GL_TEXTURE_CUBE_MAP_NEGATIVE_X,0,GL_RGBA8,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)

        with Image.open(f"{filepath}_front.png", mode = "r") as img:
            image_width,image_height = img.size
            img = img.rotate(90)
            img = img.convert('RGBA')
            img_data = bytes(img.tobytes())
            glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X,0,GL_RGBA8,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP,self.texture)

    def destroy(self):
        glDeleteTextures(1, (self.texture,))

class GameRenderer:


    def __init__(self, window):

        self.create_assets()
        
        self.create_shaders()

        self.set_onetime_shader_data()

        self.query_shader_locations()

        self.set_up_opengl(window)
    
    def create_shaders(self):

        self.shader3DColored = createShader("shaders/vertex_3d_colored.txt",
                                            "shaders/fragment_3d_colored.txt")
    
        self.shader3DCubemap = createShader("shaders/vertex_3d_cubemap.txt",
                                        "shaders/fragment_3d_cubemap.txt")

    def set_onetime_shader_data(self):

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = SCREEN_WIDTH/SCREEN_HEIGHT, 
            near = 0.1, far = 200, dtype=np.float32
        )

        glUseProgram(self.shader3DColored)
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader3DColored,"projection"),
            1,GL_FALSE,projection_transform
        )

        glUseProgram(self.shader3DCubemap)
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader3DCubemap,"projection"),
            1,GL_FALSE,projection_transform
        )
        glUniform1i(glGetUniformLocation(self.shader3DCubemap, "skyBox"), 0)
    
    def query_shader_locations(self):

        self.model_location = {}
        self.view_location = {}

        glUseProgram(self.shader3DColored)
        self.model_location["colored"] = glGetUniformLocation(self.shader3DColored, "model")
        self.view_location["colored"] = glGetUniformLocation(self.shader3DColored, "view")
        self.color_location = glGetUniformLocation(self.shader3DColored, "objectColor")
        self.alpha_location = glGetUniformLocation(self.shader3DColored, "alpha")

        glUseProgram(self.shader3DCubemap)
        self.model_location["cubemap"] = glGetUniformLocation(self.shader3DCubemap, "model")
        self.view_location["cubemap"] = glGetUniformLocation(self.shader3DCubemap, "view")

    def create_assets(self):

        self.player_debug_model = ObjModel("models", "player_mask.obj")
        self.ground_debug_model = ObjModel("models", "ground.obj")
        self.skyBoxMaterial = CubeMapMaterial("gfx/sky")
        self.skyBoxModel = CubeMapModel(200, 200, 200)
        self.block_debug_model = CubeMapModel(8, 8, 1)
        self.static_geometry_model = StaticGeometry()
    
    def bake_geometry(self, blocks: list[model.Block]) -> None:

        for block in blocks:
            self.static_geometry_model.consume(
                self.block_debug_model.positions,
                self.block_debug_model.normals,
                block.modelTransform
            )
        
        self.static_geometry_model.finalize()
        
        self.block_debug_model.destroy()

    def set_up_opengl(self, window) -> None:

        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_CUBE_MAP_SEAMLESS)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        (w, h) = glfw.get_framebuffer_size(window)
        glViewport(0, 0, w, h)
        glClearColor(0.1, 0.1, 0.1, 1)

    def render(self, scene):
        
        glUseProgram(self.shader3DCubemap)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        modelTransform = pyrr.matrix44.create_identity(dtype = np.float32)
        modelTransform = pyrr.matrix44.multiply(
            m1 = modelTransform,
            m2 = pyrr.matrix44.create_from_translation(
                vec = scene.player.box.center - np.array([0,0,0.9], dtype=np.float32), 
                dtype = np.float32
            )
        )
        glUniformMatrix4fv(self.model_location["cubemap"], 1, GL_FALSE, modelTransform)
        glUniformMatrix4fv(self.view_location["cubemap"], 1, GL_FALSE, scene.camera.viewTransform)
        self.skyBoxMaterial.use()
        glBindVertexArray(self.skyBoxModel.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.skyBoxModel.vertex_count)
        
        glUseProgram(self.shader3DColored)
        glEnable(GL_CULL_FACE)
        glUniform1f(self.alpha_location, 1.0)
        
        glUniformMatrix4fv(self.view_location["colored"], 1, GL_FALSE, scene.camera.viewTransform)

        #ground model
        glBindVertexArray(self.ground_debug_model.vao)
        glEnable(GL_CULL_FACE)
        glUniformMatrix4fv(
            self.model_location["colored"], 1, GL_FALSE, 
            pyrr.matrix44.create_from_translation(
                vec = np.array(
                    [
                        scene.player.box.center[0],
                        scene.player.box.center[1],
                        0
                    ], dtype=np.float32
                )
            )
        )
        glUniform3fv(self.color_location, 1, np.array([0.5, 0.5, 0.5], dtype=np.float32))
        glDrawArrays(GL_TRIANGLES, 0, self.ground_debug_model.vertex_count)

        #static geometry
        glBindVertexArray(self.static_geometry_model.vao)
        glUniformMatrix4fv(
            self.model_location["colored"], 1, GL_FALSE, 
            pyrr.matrix44.create_identity()
        )
        glUniform3fv(self.color_location, 1, np.array([0.5, 0.5, 1.0], dtype=np.float32))
        glDrawArrays(GL_TRIANGLES, 0, self.static_geometry_model.vertex_count)
        
        #player
        glUniformMatrix4fv(self.model_location["colored"], 1, GL_FALSE, scene.player.modelTransform)
        glUniform3fv(self.color_location, 1, scene.player.color)
        cam_to_player_dist = pyrr.vector.length(scene.camera.position - scene.player.box.center)
        if cam_to_player_dist < 3.2:
            alpha = max(0.0, (1.0 - abs(cam_to_player_dist / 1.6))**2)
            glUniform1f(self.alpha_location, alpha)
        glBindVertexArray(self.player_debug_model.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.player_debug_model.vertex_count)
        glEnable(GL_CULL_FACE)

        glFlush()

    def destroy(self):

        self.player_debug_model.destroy()
        self.ground_debug_model.destroy()
        self.skyBoxMaterial.destroy()
        self.static_geometry_model.destroy()
        
        glDeleteProgram(self.shader3DColored)
        glDeleteProgram(self.shader3DCubemap)
