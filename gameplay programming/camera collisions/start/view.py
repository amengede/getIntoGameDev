from config import *
import geometry

class ObjModel:


    def __init__(self, folderpath, filename):
        
        self.vertices = np.array(
            load_model_from_file(folderpath, filename),
            dtype=np.float32
        )

        #vertex array object, all that stuff
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,self.vbo)
        glBufferData(GL_ARRAY_BUFFER,self.vertices.nbytes,self.vertices,GL_STATIC_DRAW)
        self.vertex_count = int(len(self.vertices)/8)

        #position attribute
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,self.vertices.itemsize*8,ctypes.c_void_p(0))
        #normal attribute
        #glEnableVertexAttribArray(1)
        #glVertexAttribPointer(1,2,GL_FLOAT,GL_FALSE,self.vertices.itemsize*8,ctypes.c_void_p(12))
        #texture attribute
        #glEnableVertexAttribArray(2)
        #glVertexAttribPointer(2,3,GL_FLOAT,GL_FALSE,self.vertices.itemsize*8,ctypes.c_void_p(20))
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

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

class CubeMapModel:

    
    def __init__(self, l, w, h):

        # x, y, z
        self.vertices = (
            
            -l/2,  w/2, -h/2,
             l/2,  w/2, -h/2,
            -l/2, -w/2, -h/2,

             l/2,  w/2, -h/2,
             l/2, -w/2, -h/2,
            -l/2, -w/2, -h/2,

             l/2,  w/2,  h/2,
            -l/2,  w/2,  h/2,
            -l/2, -w/2,  h/2,

            -l/2, -w/2,  h/2,
             l/2, -w/2,  h/2,
             l/2,  w/2,  h/2,

            -l/2, -w/2,  h/2,
            -l/2,  w/2,  h/2,
            -l/2,  w/2, -h/2,

            -l/2,  w/2, -h/2,
            -l/2, -w/2, -h/2,
            -l/2, -w/2,  h/2,

             l/2, -w/2, -h/2,
             l/2,  w/2, -h/2,
             l/2,  w/2,  h/2,

             l/2,  w/2,  h/2,
             l/2, -w/2,  h/2,
             l/2, -w/2, -h/2,

             l/2, -w/2,  h/2,
            -l/2, -w/2,  h/2,
            -l/2, -w/2, -h/2,

            -l/2, -w/2, -h/2,
             l/2, -w/2, -h/2,
             l/2, -w/2,  h/2,

             l/2,  w/2, -h/2,
            -l/2,  w/2, -h/2,
            -l/2,  w/2,  h/2,

            -l/2,  w/2,  h/2,
             l/2,  w/2,  h/2,
             l/2,  w/2, -h/2,
        )
        self.vertex_count = len(self.vertices)//3
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

    def destroy(self):

        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class CubeWireframeModel:

    
    def __init__(self, l, w, h):

        # x, y, z
        self.vertices = (
            -l / 2, -w / 2, -h / 2,  l / 2, -w / 2, -h / 2,
            -l / 2, -w / 2, -h / 2, -l / 2,  w / 2, -h / 2,
            -l / 2, -w / 2, -h / 2, -l / 2, -w / 2,  h / 2,

             l / 2, -w / 2, -h / 2,  l / 2,  w / 2, -h / 2,
             l / 2, -w / 2, -h / 2,  l / 2, -w / 2,  h / 2,

            -l / 2,  w / 2, -h / 2,  l / 2,  w / 2, -h / 2,
            -l / 2,  w / 2, -h / 2, -l / 2,  w / 2,  h / 2,

             l / 2,  w / 2, -h / 2,  l / 2,  w / 2,  h / 2,

            -l / 2, -w / 2,  h / 2,  l / 2, -w / 2,  h / 2,
            -l / 2, -w / 2,  h / 2, -l / 2,  w / 2,  h / 2,

             l / 2,  w / 2,  h / 2, -l / 2,  w / 2,  h / 2,
             l / 2,  w / 2,  h / 2,  l / 2, -w / 2,  h / 2,
        )
        self.vertex_count = len(self.vertices)//3
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

    def destroy(self):

        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class GameRenderer:


    def __init__(self, window):

        self.window = window

        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_CUBE_MAP_SEAMLESS)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        self.create_shaders()
        self.set_onetime_shader_data()
        self.query_shader_locations()

        self.create_assets()
    
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

        glUseProgram(self.shader3DCubemap)
        self.model_location["cubemap"] = glGetUniformLocation(self.shader3DCubemap, "model")
        self.view_location["cubemap"] = glGetUniformLocation(self.shader3DCubemap, "view")

    def create_assets(self):

        self.player_debug_model = ObjModel("models", "player_mask.obj")
        self.ground_debug_model = ObjModel("models", "ground.obj")
        self.skyBoxMaterial = CubeMapMaterial("img/sky")
        self.skyBoxModel = CubeMapModel(200, 200, 200)
        self.block_debug_model = CubeMapModel(8, 8, 1)
        self.grid_debug_model = CubeWireframeModel(
            geometry.grid.length,
            geometry.grid.width,
            geometry.grid.height
        )

    def render(self, scene):

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        
        glUseProgram(self.shader3DCubemap)
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
        
        glUniformMatrix4fv(self.view_location["colored"], 1, GL_FALSE, scene.camera.viewTransform)

        glUniformMatrix4fv(self.model_location["colored"], 1, GL_FALSE, scene.ground.modelTransform)
        glUniform3fv(self.color_location, 1, np.array([0.5, 0.5, 1.0], dtype=np.float32))
        glBindVertexArray(self.ground_debug_model.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.ground_debug_model.vertex_count)

        glBindVertexArray(self.block_debug_model.vao)
        glEnable(GL_CULL_FACE)
        for block in scene.blocks:

            glUniformMatrix4fv(self.model_location["colored"], 1, GL_FALSE, block.modelTransform)
            glUniform3fv(self.color_location, 1, block.color)
            glDrawArrays(GL_TRIANGLES, 0, self.block_debug_model.vertex_count)
            
        glUniformMatrix4fv(self.model_location["colored"], 1, GL_FALSE, scene.player.modelTransform)
        glUniform3fv(self.color_location, 1, scene.player.color)
        glBindVertexArray(self.player_debug_model.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.player_debug_model.vertex_count)
        glEnable(GL_CULL_FACE)

        #glfw.swap_buffers(self.window)
        glFlush()

    def destroy(self):

        self.player_debug_model.destroy()
        self.ground_debug_model.destroy()
        self.skyBoxMaterial.destroy()
        self.skyBoxModel.destroy()
        
        glDeleteProgram(self.shader3DColored)
        glDeleteProgram(self.shader3DCubemap)