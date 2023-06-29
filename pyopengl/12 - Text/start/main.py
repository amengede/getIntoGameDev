############################## Imports   ######################################
#region
import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
from PIL import Image
#endregion
############################## Constants ######################################
#region
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

GLOBAL_X = np.array([1,0,0], dtype=np.float32)
GLOBAL_Y = np.array([0,1,0], dtype=np.float32)
GLOBAL_Z = np.array([0,0,1], dtype=np.float32)

ENTITY_TYPE = {
    "CUBE": 0,
    "POINTLIGHT": 1,
    "MEDKIT": 2,
    "SCREEN": 3,
}

UNIFORM_TYPE = {
    "AMBIENT": 0,
    "VIEW": 1,
    "PROJECTION": 2,
    "CAMERA_POS": 3,
    "LIGHT_COLOR": 4,
    "LIGHT_POS": 5,
    "LIGHT_STRENGTH": 6,
    "TINT": 7,
    "MODEL": 8,
}

PIPELINE_TYPE = {
    "STANDARD": 0,
    "EMISSIVE": 1,
    "POST": 2,
    "BLIT": 3,
    "CRT": 4,
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
####################### Model #################################################
#region
class Entity:
    """
        A basic object in the world, with a position and rotation.
    """
    __slots__ = ("position", "eulers")


    def __init__(self, position: list[float], eulers: list[float]):
        """
            Initialize the entity.

            Parameters:

                position: the position of the entity.

                eulers: the rotation of the entity
                        about each axis.
        """

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)

    def update(self, dt: float, camera_pos: np.ndarray) -> None:
        """
            Update the object, this is meant to be implemented by
            objects extending this class.

            Parameters:

                dt: framerate correction factor.

                camera_pos: the player's position.
        """

        pass

    def get_model_transform(self) -> np.ndarray:
        """
            Returns the entity's model to world
            transformation matrix.
        """

        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)

        model_transform = pyrr.matrix44.multiply(
            m1=model_transform, 
            m2=pyrr.matrix44.create_from_axis_rotation(
                axis = GLOBAL_Y,
                theta = np.radians(self.eulers[1]), 
                dtype = np.float32
            )
        )

        model_transform = pyrr.matrix44.multiply(
            m1=model_transform, 
            m2=pyrr.matrix44.create_from_axis_rotation(
                axis = GLOBAL_Z,
                theta = np.radians(self.eulers[2]), 
                dtype = np.float32
            )
        )

        return pyrr.matrix44.multiply(
            m1=model_transform, 
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self.position),dtype=np.float32
            )
        )
        
class Cube(Entity):
    """
        A basic object in the world, with a position and rotation.
    """
    __slots__ = ("euler_velocity",)


    def __init__(self, position: list[float], eulers: list[float]):
        """
            Initialize the cube.

            Parameters:

                position: the position of the entity.

                eulers: the rotation of the entity
                        about each axis.
                
                euler_velocity: the angular velocity of the cube. 
        """

        super().__init__(position, eulers)

class BillBoard(Entity):
    """
        An object which always faces towards the camera
    """
    __slots__ = tuple()


    def __init__(self, position: list[float]):
        """
            Initialize the billboard.

            Parameters:

                position: the position of the entity.
        """

        super().__init__(position, eulers=[0,0,0])
    
    def update(self, dt: float, camera_pos: np.ndarray) -> None:
        """
            Update the billboard.

            Parameters:

                dt: framerate correction factor.

                camera_pos: the position of the camera in the scene
        """

        self_to_camera = camera_pos - self.position
        self.eulers[2] = -np.degrees(np.arctan2(-self_to_camera[1], self_to_camera[0]))
        dist2d = pyrr.vector.length(self_to_camera)
        self.eulers[1] = -np.degrees(np.arctan2(self_to_camera[2], dist2d))

class PointLight(BillBoard):
    """
        A simple pointlight.
    """
    __slots__ = ("color", "strength")


    def __init__(
        self, position: list[float], 
        color: list[float], strength: float):
        """
            Initialize the light.

            Parameters:

                position: position of the light.

                color: (r,g,b) color of the light.

                strength: strength of the light.
        """

        super().__init__(position)
        self.color = np.array(color, dtype=np.float32)
        self.strength = strength

class Camera(Entity):
    """
        A first person camera.
    """
    __slots__ = ("forwards", "right", "up")


    def __init__(self, position: list[float]):
        """
            Initialize the camera.

            Parameters:

                position: the camera's position
        """

        super().__init__(position, eulers = [0,0,0])
        self.update()
    
    def update(self) -> None:
        """
            Update the camera.
        """

        theta = self.eulers[2]
        phi = self.eulers[1]

        self.forwards = np.array(
            [
                np.cos(np.deg2rad(theta)) * np.cos(np.deg2rad(phi)),
                np.sin(np.deg2rad(theta)) * np.cos(np.deg2rad(phi)),
                np.sin(np.deg2rad(phi))
            ],
            dtype = np.float32
        )

        self.right = np.cross(self.forwards, GLOBAL_Z)

        self.up = np.cross(self.right, self.forwards)

    def get_view_transform(self) -> np.ndarray:
        """
            Returns the camera's world to view
            transformation matrix.
        """

        return pyrr.matrix44.create_look_at(
            eye = self.position,
            target = self.position + self.forwards,
            up = self.up, dtype = np.float32)
    
    def move(self, d_pos) -> None:
        """
            Move by the given amount in the (forwards, right, up) vectors.
        """

        self.position += d_pos[0] * self.forwards \
                        + d_pos[1] * self.right \
                        + d_pos[2] * self.up

        self.position[2] = 2.0
    
    def spin(self, d_eulers) -> None:
        """
            Spin the camera by the given amount about the (x, y, z) axes.
        """

        self.eulers += d_eulers

        self.eulers[0] %= 360
        self.eulers[1] = min(89, max(-89, self.eulers[1]))
        self.eulers[2] %= 360

class Scene:
    """
        Manages all objects and coordinates their interactions.
    """
    __slots__ = ("entities", "player", "lights")


    def __init__(self):
        """
            Initialize the scene.
        """

        self.entities: dict[int, list[Entity]] = {
            ENTITY_TYPE["CUBE"]: [
                Cube(
                    position = [6,0,1],
                    eulers = [0,0,0]),],
            ENTITY_TYPE["MEDKIT"]: [
                BillBoard(position = [3,0,0.5])
            ]
        }

        self.lights: list[PointLight] = [
            PointLight(
                position = [4.0, -4.0 + i, 1.0],
                color = [
                    np.random.uniform(low=0.0, high=1.0), 
                    np.random.uniform(low=0.0, high=1.0), 
                    np.random.uniform(low=0.0, high=1.0)
                ],
                strength = 3)
            for i in range(8)
        ]

        self.player = Camera(
            position = [0,0,2]
        )

    def update(self, rate: float) -> None:
        """
            Update all objects in the scene.

            Parameters:

                rate: framerate correction factor
        """

        for entities in self.entities.values():
            for entity in entities:
                entity.update(rate, self.player.position)

        for light in self.lights:
            light.update(rate, self.player.position)
        
        self.player.update()
    
    def move_player(self, d_pos: np.ndarray) -> None:
        """
            move the player by the given amount in the 
            (forwards, right, up) vectors.
        """

        self.player.move(d_pos)
    
    def spin_player(self, d_eulers: list[float]) -> None:
        """
            spin the player by the given amount
            around the (x,y,z) axes
        """

        self.player.spin(d_eulers)
#endregion
####################### Control ###############################################
#region
class App:
    """
        The control class.
    """
    __slots__ = (
        "window", "renderer", "scene", "last_time", 
        "current_time", "frames_rendered", "frametime",
        "_keys")


    def __init__(self):
        """
            Initialize the program.
        """

        self._set_up_glfw()

        self._set_up_timer()

        self._set_up_input_systems()

        self._create_assets()
    
    def _set_up_glfw(self) -> None:
        """
            Initialize and configure GLFW
        """

        glfw.init()
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR,4)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR,3)
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, 
            GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, GLFW_CONSTANTS.GLFW_TRUE)
        #for uncapped framerate
        glfw.window_hint(GLFW_CONSTANTS.GLFW_DOUBLEBUFFER,GL_FALSE) 
        self.window = glfw.create_window(
            SCREEN_WIDTH, SCREEN_HEIGHT, "Title", None, None)
        glfw.make_context_current(self.window)
    
    def _set_up_timer(self) -> None:
        """
            Initialize the variables used by the framerate
            timer.
        """

        self.last_time = glfw.get_time()
        self.current_time = 0
        self.frames_rendered = 0
        self.frametime = 0.0
    
    def _set_up_input_systems(self) -> None:
        """
            Configure the mouse and keyboard
        """

        glfw.set_input_mode(
            self.window, 
            GLFW_CONSTANTS.GLFW_CURSOR, 
            GLFW_CONSTANTS.GLFW_CURSOR_HIDDEN
        )

        self._keys = {}
        glfw.set_key_callback(self.window, self._key_callback)
    
    def _key_callback(self, window, key, scancode, action, mods) -> None:
        """
            Handle a key event.

            Parameters:

                window: the window on which the keypress occurred.

                key: the key which was pressed

                scancode: scancode of the key

                action: action of the key event

                mods: modifiers applied to the event
        """

        state = False
        match action:
            case GLFW_CONSTANTS.GLFW_PRESS:
                state = True
            case GLFW_CONSTANTS.GLFW_RELEASE:
                state = False
            case _:
                return

        self._keys[key] = state
    
    def _create_assets(self) -> None:
        """
            Create all of the assets needed by the program.
        """

        self.renderer = GraphicsEngine()

        self.scene = Scene()

    def run(self) -> None:
        """
            Run the program.
        """

        running = True
        while (running):
            #check events
            if glfw.window_should_close(self.window) \
                or self._keys.get(GLFW_CONSTANTS.GLFW_KEY_ESCAPE, False):
                running = False
            
            self._handle_keys()
            self._handle_mouse()

            glfw.poll_events()

            self.scene.update(self.frametime / 16.67)
            
            self.renderer.render(
                self.scene.player, self.scene.entities, self.scene.lights)

            #timing
            self._calculate_framerate()

    def _handle_keys(self) -> None:
        """
            Takes action based on the keys currently pressed.
        """

        rate = 0.005*self.frametime
        d_pos = np.zeros(3, dtype=np.float32)

        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_W, False):
            d_pos += GLOBAL_X
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_A, False):
            d_pos -= GLOBAL_Y
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_S, False):
            d_pos -= GLOBAL_X
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_D, False):
            d_pos += GLOBAL_Y

        length = pyrr.vector.length(d_pos)

        if abs(length) < 0.00001:
            return

        d_pos = rate * d_pos / length

        self.scene.move_player(d_pos)

    def _handle_mouse(self) -> None:
        """
            spin the player based on the mouse movement
        """

        (x,y) = glfw.get_cursor_pos(self.window)
        d_eulers = 0.02 * ((SCREEN_WIDTH / 2) - x) * GLOBAL_Z
        d_eulers += 0.02 * ((SCREEN_HEIGHT / 2) - y) * GLOBAL_Y
        self.scene.spin_player(d_eulers)
        glfw.set_cursor_pos(self.window, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    def _calculate_framerate(self) -> None:
        """
            Calculate the framerate and frametime,
            and update the window title.
        """

        self.current_time = glfw.get_time()
        delta = self.current_time - self.last_time
        if (delta >= 1):
            framerate = max(1,int(self.frames_rendered/delta))
            glfw.set_window_title(self.window, f"Running at {framerate} fps.")
            self.last_time = self.current_time
            self.frames_rendered = -1
            self.frametime = float(1000.0 / max(1,framerate))
        self.frames_rendered += 1

    def quit(self):
        
        self.renderer.destroy()
#endregion
####################### View  #################################################
#region
class GraphicsEngine:
    """
        Draws entities and stuff.
    """
    __slots__ = ("meshes", "materials", "shaders", "framebuffers")


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

        glClearColor(0.0, 0.0, 0.0, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    def _create_assets(self) -> None:
        """
            Create all of the assets needed for drawing.
        """

        self.meshes: dict[int, Mesh] = {
            ENTITY_TYPE["CUBE"]: ObjMesh("models/cube.obj"),
            ENTITY_TYPE["MEDKIT"]: BillBoardMesh(w = 0.6, h = 0.5),
            ENTITY_TYPE["POINTLIGHT"]: BillBoardMesh(w = 0.2, h = 0.1),
            ENTITY_TYPE["SCREEN"]: TexturedQuad(0, 0, 2, 2),
        }

        self.framebuffers: list[FrameBuffer] = [
            FrameBuffer((ColorAttachment(),), DepthStencilAttachment()),
            FrameBuffer((ColorAttachment(),), DepthStencilAttachment()),
        ]

        self.materials: dict[int, Material] = {
            ENTITY_TYPE["CUBE"]: AdvancedMaterial("wood", "png"),
            ENTITY_TYPE["MEDKIT"]: AdvancedMaterial("medkit", "png"),
            ENTITY_TYPE["POINTLIGHT"]: Material2D("gfx/greenlight.png", 0),
        }

        self.shaders: dict[int, Shader] = {
            PIPELINE_TYPE["STANDARD"]: Shader(
                "shaders/vertex.txt", 
                "shaders/fragment.txt"),
            PIPELINE_TYPE["EMISSIVE"]: Shader(
                "shaders/vertex_light.txt", 
                "shaders/fragment_light.txt"),
            PIPELINE_TYPE["POST"]: Shader(
                "shaders/simple_post_vertex.txt", 
                "shaders/post_fragment.txt"),
            PIPELINE_TYPE["CRT"]: Shader(
                "shaders/simple_post_vertex.txt", 
                "shaders/crt_fragment.txt"),
            PIPELINE_TYPE["BLIT"]: Shader(
                "shaders/simple_post_vertex.txt", 
                "shaders/screen_fragment.txt"),
        }
    
    def _set_onetime_uniforms(self) -> None:
        """
            Some shader data only needs to be set once.
        """

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = SCREEN_WIDTH/SCREEN_HEIGHT, 
            near = 0.1, far = 50, dtype=np.float32
        )

        shader_type = PIPELINE_TYPE["STANDARD"]
        shader = self.shaders[shader_type]
        shader.use()

        glUniformMatrix4fv(
            glGetUniformLocation(shader.program, "projection"),
            1, GL_FALSE, projection_transform
        )
        glUniform1i(
            glGetUniformLocation(shader.program, "material.albedo"), 0)
        glUniform1i(
            glGetUniformLocation(shader.program, "material.ao"), 1)
        glUniform1i(
            glGetUniformLocation(shader.program, "material.specular"), 3)
        glUniform1i(
            glGetUniformLocation(shader.program, "material.normal"), 2)

        shader_type = PIPELINE_TYPE["EMISSIVE"]
        shader = self.shaders[shader_type]
        shader.use()

        glUniformMatrix4fv(
            glGetUniformLocation(shader.program,"projection"),
            1, GL_FALSE, projection_transform
        )

    def _get_uniform_locations(self) -> None:
        """
            Query and store the locations of shader uniforms
        """

        shader_type = PIPELINE_TYPE["STANDARD"]
        shader = self.shaders[shader_type]
        shader.use()

        shader.cache_single_location(UNIFORM_TYPE["MODEL"], "model")
        shader.cache_single_location(UNIFORM_TYPE["VIEW"], "view")
        shader.cache_single_location(
            UNIFORM_TYPE["CAMERA_POS"], "viewPos")
        
        for i in range(8):
            shader.cache_multi_location(
                UNIFORM_TYPE["LIGHT_COLOR"], f"lights[{i}].color")
            shader.cache_multi_location(
                UNIFORM_TYPE["LIGHT_POS"], f"lights[{i}].pos")
            shader.cache_multi_location(
                UNIFORM_TYPE["LIGHT_STRENGTH"], f"lights[{i}].strength")
            
        shader_type = PIPELINE_TYPE["EMISSIVE"]
        shader = self.shaders[shader_type]
        shader.use()

        shader.cache_single_location(UNIFORM_TYPE["MODEL"], "model")
        shader.cache_single_location(UNIFORM_TYPE["VIEW"], "view")
        shader.cache_single_location(UNIFORM_TYPE["TINT"], "tint")

    def render(self, 
        camera: Camera, 
        renderables: dict[int, list[Entity]],
        lights: list[PointLight]) -> None:
        """
            Draw everything.

            Parameters:

                camera: the scene's camera

                renderables: all the entities to draw

                lights: all the lights in the scene
        """
        
        view = camera.get_view_transform()

        #First pass
        self.framebuffers[0].use()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

        #lit shader
        shader_type = PIPELINE_TYPE["STANDARD"]
        shader = self.shaders[shader_type]
        shader.use()

        glUniformMatrix4fv(
            shader.fetch_single_location(UNIFORM_TYPE["VIEW"]), 
            1, GL_FALSE, view)

        glUniform3fv(
            shader.fetch_single_location(UNIFORM_TYPE["CAMERA_POS"]), 
            1, camera.position)

        for i,light in enumerate(lights):
            glUniform3fv(
                shader.fetch_multi_location(UNIFORM_TYPE["LIGHT_POS"], i),
                1, light.position)
            glUniform3fv(
                shader.fetch_multi_location(UNIFORM_TYPE["LIGHT_COLOR"], i),
                1, light.color)
            glUniform1f(
                shader.fetch_multi_location(UNIFORM_TYPE["LIGHT_STRENGTH"], i),
                light.strength)

        for entity_type, entities in renderables.items():

            if entity_type not in self.meshes:
                continue
            mesh = self.meshes[entity_type]
            mesh.arm_for_drawing()
            self.materials[entity_type].use()

            for entity in entities:
                glUniformMatrix4fv(
                    shader.fetch_single_location(UNIFORM_TYPE["MODEL"]), 
                    1, GL_FALSE, entity.get_model_transform())
                mesh.draw()

        #unlit shader
        shader_type = PIPELINE_TYPE["EMISSIVE"]
        shader = self.shaders[shader_type]
        shader.use()

        glUniformMatrix4fv(
            shader.fetch_single_location(UNIFORM_TYPE["VIEW"]), 
            1, GL_FALSE, view)

        mesh = self.meshes[ENTITY_TYPE["POINTLIGHT"]]
        mesh.arm_for_drawing()
        self.materials[ENTITY_TYPE["POINTLIGHT"]].use()
        
        for light in lights:

            glUniformMatrix4fv(
                shader.fetch_single_location(UNIFORM_TYPE["MODEL"]), 
                1, GL_FALSE, light.get_model_transform())
            glUniform3fv(
                shader.fetch_single_location(UNIFORM_TYPE["TINT"]),
                1, light.color)
            mesh.draw()
        
        #Post processing pass
        shader_type = PIPELINE_TYPE["POST"]
        shader = self.shaders[shader_type]
        shader.use()
        self.framebuffers[1].use()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)
        self.framebuffers[0].color_attachments[0].use(0)
        mesh = self.meshes[ENTITY_TYPE["SCREEN"]]
        mesh.arm_for_drawing()
        mesh.draw()

        #Blit color buffer 1 onto color buffer 0
        shader_type = PIPELINE_TYPE["BLIT"]
        shader = self.shaders[shader_type]
        shader.use()
        self.framebuffers[0].use()
        self.framebuffers[1].color_attachments[0].use(0)
        mesh.draw()
        
        #CRT emulation pass
        shader_type = PIPELINE_TYPE["CRT"]
        shader = self.shaders[shader_type]
        shader.use()
        self.framebuffers[1].use()
        self.framebuffers[0].color_attachments[0].use(0)
        mesh.draw()
        
        #Put the final result on screen
        shader_type = PIPELINE_TYPE["BLIT"]
        shader = self.shaders[shader_type]
        shader.use()
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        self.framebuffers[1].color_attachments[0].use(0)
        mesh.draw()

        glFlush()

    def destroy(self) -> None:
        """ free any allocated memory """

        for framebuffer in self.framebuffers:
            framebuffer.destroy()
        for mesh in self.meshes.values():
            mesh.destroy()
        for material in self.materials.values():
            material.destroy()
        for shader in self.shaders.values():
            shader.destroy()

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
            Material2D(f"gfx/{filename}_albedo.{filetype}", 0),
            Material2D(f"gfx/{filename}_ao.{filetype}", 1),
            Material2D(f"gfx/{filename}_normal.{filetype}", 2),
            Material2D(f"gfx/{filename}_glossmap.{filetype}", 3),
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

class ColorAttachment:
    """
        A color buffer which can be attached to a framebuffer.
    """
    __slots__ = ("texture",)


    def __init__(self):
        """
            Initialize the color buffer.
        """

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexStorage2D(GL_TEXTURE_2D, 1, GL_RGBA8, SCREEN_WIDTH, SCREEN_HEIGHT)
        glBindTexture(GL_TEXTURE_2D, 0)
    
    def use(self, unit: int) -> None:
        """
            Bind the texture to the given unit.
        """

        glActiveTexture(GL_TEXTURE0 + unit)
        glBindTexture(GL_TEXTURE_2D, self.texture)
    
    def destroy(self) -> None:
        """
            Free the memory.
        """

        glDeleteTextures(1, (self.texture,))

class DepthStencilAttachment:
    """
        A simple renderbuffer which can be used as a depth attachment.
    """
    __slots__ = ("render_buffer",)


    def __init__(self):
        """
            Initialize the buffer.
        """

        self.render_buffer = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, self.render_buffer)
        glRenderbufferStorage(
            GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, SCREEN_WIDTH, SCREEN_HEIGHT
        )
        glBindRenderbuffer(GL_RENDERBUFFER,0)

    def destroy(self) -> None:
        """
            Free any allocated memory.
        """

        glDeleteRenderbuffers(1, (self.render_buffer,))

class FrameBuffer:
    """
        A framebuffer!
    """
    __slots__ = ("fbo", "color_attachments", "depth_attachment")


    def __init__(self, 
        color_attachments: tuple[ColorAttachment], 
        depth_attachment: DepthStencilAttachment):
        """
            Create a framebuffer with the given attachments.
        """

        self.fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        
        self.color_attachments = color_attachments
        for i,color_buffer in enumerate(color_attachments):
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0 + i, 
                GL_TEXTURE_2D, color_buffer.texture, 0)
        
        self.depth_attachment = depth_attachment
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, 
            GL_RENDERBUFFER, depth_attachment.render_buffer)

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
    
    def use(self) -> None:
        """
            Bind the framebuffer for drawing.
        """

        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
    
    def destroy(self) -> None:
        """
            Destroy the framebuffer and all its attachments.
        """

        glDeleteFramebuffers(1, (self.fbo,))
        
        for color_buffer in self.color_attachments:
            color_buffer.destroy()
        
        self.depth_attachment.destroy()

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

    def destroy(self) -> None:
        """
            Free any allocated memory.
        """
        
        glDeleteVertexArrays(1,(self.vao,))
        glDeleteBuffers(1,(self.vbo,))

class ObjMesh(Mesh):
    """
        A mesh which is initialized from an obj file.
    """
    __slots__ = tuple()


    def __init__(self, filename: str):
        """
            Initialize the mesh.
        """

        super().__init__()
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

class BillBoardMesh(Mesh):
    """
        A mesh which represents a billboard.
    """
    __slots__ = tuple()


    def __init__(self, w: float, h: float):
        """
            Initialize the mesh.
        """
        
        super().__init__()
        vertices = (
            0, -w/2,  h/2, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0,
            0, -w/2, -h/2, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0,
            0,  w/2, -h/2, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0,

            0, -w/2,  h/2, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0,
            0,  w/2, -h/2, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0,
            0,  w/2,  h/2, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0
        )
        vertices = np.array(vertices, dtype=np.float32)
        self.vertex_count = 6
        
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

class TexturedQuad(Mesh):
    """
        A 2D Quad with texture coordinates
    """
    __slots__ = tuple()


    def __init__(self, x: float, y: float, w: float, h: float):
        
        super().__init__()
        vertices = (
            x - w / 2, y + h / 2, 0, 1,
            x - w / 2, y - h / 2, 0, 0,
            x + w / 2, y - h / 2, 1, 0,

            x - w / 2, y + h / 2, 0, 1,
            x + w / 2, y - h / 2, 1, 0,
            x + w / 2, y + h / 2, 1, 1
        )
        vertices = np.array(vertices, dtype=np.float32)

        self.vertex_count = 6
        
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(8))
#endregion
###############################################################################
my_app = App()
my_app.run()
my_app.quit()