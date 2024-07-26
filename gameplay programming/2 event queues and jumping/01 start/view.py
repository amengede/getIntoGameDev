from config import *
import model

class Mesh:
    """ A general mesh """


    def __init__(self):
        """
            Create the mesh.
        """

        self._vertex_count = 0

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
    
    def destroy(self) -> None:
        """
            Destroy the mesh, freeing any allocated memory.
        """
        
        glDeleteVertexArrays(1, (self._vao,))
        glDeleteBuffers(1,(self._vbo,))

class ObjMesh(Mesh):
    """
        A mesh which can be loaded from a file.
    """


    def __init__(self, folderpath: str, filename: str):
        """
            Initialize the mesh, loading from the file.

            Parameters:

                folderpath: the folder to load from

                filename: the filename in the folder
        """

        super().__init__()
        
        vertices = np.array(
            load_model_from_file(folderpath, filename),
            dtype=np.float32
        )

        glBindVertexArray(self._vao)

        glBindBuffer(GL_ARRAY_BUFFER,self._vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        self._vertex_count = int(len(vertices)/6)

        #position attribute
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, vertices.itemsize*6, ctypes.c_void_p(0))
        #normal attribute
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, vertices.itemsize*6, ctypes.c_void_p(12))

class CuboidMesh(Mesh):
    """
        A cuboid of given dimensions.
    """

    
    def __init__(self, l: float, w: float, h: float):
        """
            Create a cuboid of the given dimensions.
        """

        super().__init__()

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

        #position attribute
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, vertices.itemsize*6, ctypes.c_void_p(0))
        #normal attribute
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, vertices.itemsize*6, ctypes.c_void_p(12))

class Quad2D(Mesh):


    def __init__(self, center: tuple[float], size: tuple[float]):

        super().__init__()

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
        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))

class Material:
    """
        A texture of some kind.
    """


    def __init__(self, texture_type: int, texture_unit: int):
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

class CubemapMaterial(Material):
    """
        A cubemap texture.
    """


    def __init__(self, filepath: str):
        """
            Initialize the cubemap, loading all images.

            Parameters:

                filepath: the filepath up to the texture name.
        """

        super().__init__(GL_TEXTURE_CUBE_MAP, 0)

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

        self._query_shader_locations()
    
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
            OBJECT_TYPE_PLAYER: ObjMesh("models", "player_mask.obj"),
            OBJECT_TYPE_GROUND: ObjMesh("models", "ground.obj"),
            OBJECT_TYPE_SKY: Quad2D(center = (0.0, 0.0), size = (1.0, 1.0))
        }
        
        self._materials: dict[int, Material] = {
            OBJECT_TYPE_SKY: CubemapMaterial("gfx/sky")
        }

        self._colors: dict[int, np.ndarray] = {
            OBJECT_TYPE_PLAYER: np.array([0.8, 0.8, 0.8], dtype = np.float32),
            OBJECT_TYPE_GROUND: np.array([0.5, 0.5, 1.0], dtype = np.float32),
        }

        self._shaders: dict[int, int] = {
            PIPELINE_TYPE_SKY: createShader("shaders/vertex_3d_cubemap.txt",
                                        "shaders/fragment_3d_cubemap.txt"),
            PIPELINE_TYPE_OBJECT: createShader("shaders/vertex_3d_colored.txt",
                                            "shaders/fragment_3d_colored.txt"),
        }

    def _set_onetime_shader_data(self) -> None:
        """
            Some uniforms can be set once and forgotten.
        """

        self._projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = SCREEN_WIDTH/SCREEN_HEIGHT, 
            near = 0.1, far = 150, dtype=np.float32
        )

        shader = self._shaders[PIPELINE_TYPE_SKY]
        glUseProgram(shader)
        glUniform1i(glGetUniformLocation(shader, "skyBox"), 0)
    
    def _query_shader_locations(self):

        self._mvp_location = {}
        self._color_location = {}
        self._alpha_location = {}

        self._forwards_location = {}
        self._right_location = {}
        self._up_location = {}

        shader = self._shaders[PIPELINE_TYPE_OBJECT]
        glUseProgram(shader)
        self._mvp_location[PIPELINE_TYPE_OBJECT] = glGetUniformLocation(shader, "mvp")
        self._color_location[PIPELINE_TYPE_OBJECT] = glGetUniformLocation(shader, "color")
        self._alpha_location[PIPELINE_TYPE_OBJECT] = glGetUniformLocation(shader, "alpha")

        shader = self._shaders[PIPELINE_TYPE_SKY]
        glUseProgram(shader)
        self._forwards_location[PIPELINE_TYPE_SKY] = glGetUniformLocation(shader, "forwards")
        self._right_location[PIPELINE_TYPE_SKY] = glGetUniformLocation(shader, "right")
        self._up_location[PIPELINE_TYPE_SKY] = glGetUniformLocation(shader, "up")

    def render(self, 
        camera: model.Camera, 
        renderables: dict[int, list[model.Entity]]) -> None:
        """
            Draw the given scene.

            Parameters:

                camera: the camera object

                renderables: set of entities to draw
        """

        viewproj_transform = pyrr.matrix44.multiply(
            m1 = camera.get_view_transform(),
            m2 = self._projection_transform
        )
        forwards, right, up = camera.get_frame_of_reference()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_CULL_FACE)
        glDisable(GL_DEPTH_TEST)

        shader = self._shaders[PIPELINE_TYPE_SKY]
        glUseProgram(shader)
        material = self._materials[OBJECT_TYPE_SKY]
        mesh = self._meshes[OBJECT_TYPE_SKY]
        material.use()
        glUniform3fv(
            self._forwards_location[PIPELINE_TYPE_SKY], 
            1, forwards)
        glUniform3fv(
            self._right_location[PIPELINE_TYPE_SKY], 
            1, right)
        glUniform3fv(
            self._up_location[PIPELINE_TYPE_SKY], 
            1, SCREEN_HEIGHT / SCREEN_WIDTH * up)
        mesh.arm_for_drawing()
        mesh.draw()

        shader = self._shaders[PIPELINE_TYPE_OBJECT]
        glUseProgram(shader)
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        
        for object_type, objects in renderables.items():

            mesh = self._meshes[object_type]
            mesh.arm_for_drawing()
            glUniform3fv(
                self._color_location[PIPELINE_TYPE_OBJECT], 
                1, self._colors[object_type])
            
            for _object in objects:

                mvp_transform = pyrr.matrix44.multiply(
                    m1 = _object.get_model_transform(),
                    m2 = viewproj_transform
                )
                
                glUniformMatrix4fv(
                    self._mvp_location[PIPELINE_TYPE_OBJECT], 
                    1, GL_FALSE, mvp_transform)
                mesh.draw()

        glFlush()

    def destroy(self):

        self.player_debug_model.destroy()
        self.ground_debug_model.destroy()
        self.skyBoxMaterial.destroy()
        self.skyBoxModel.destroy()
        
        glDeleteProgram(self.shader3DColored)
        glDeleteProgram(self.shader3DCubemap)