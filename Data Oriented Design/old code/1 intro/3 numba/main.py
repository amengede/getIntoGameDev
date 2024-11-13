############################## Imports   ######################################
#region
import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
from PIL import Image
from numba import njit
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
}

PIPELINE_TYPE = {
    "STANDARD": 0,
    "EMISSIVE": 1,
}

COMPONENT_TYPE = {
    "DEFAULT": 0,
    "TRANSFORM": 1,
    "COLOR": 2,
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
############################### Data Schema ###################################
#region
"""
    Cube:
    position: 3
    eulers: 3
    euler_velocity: 3

    stride: 9
"""
"""
    Light:
    position: 3
    color: 3
    strength: 1

    stride: 7
"""
"""
    Transform:

    stride: 16
"""
"""
    Color:

    stride: 4
"""
#endregion
##################################### Model ###################################
#region
@njit(cache = True)
def update_cubes(
    cubes: np.ndarray, transforms: np.ndarray, 
    count: int, rate: float) -> None:
    """
        Update all those cubes! Also, write the transform matrices to the given array.
    """

    for i in range(count):

        #unpack cube data
        index = 9 * i
        x    = cubes[index]
        y    = cubes[index + 1]
        z    = cubes[index + 2]
        e_x  = cubes[index + 3]
        e_y  = cubes[index + 4]
        e_z  = cubes[index + 5]
        ev_x = cubes[index + 6]
        ev_y = cubes[index + 7]
        ev_z = cubes[index + 8]

        #update cube data
        e_x = (e_x + rate * ev_x) % 360
        e_y = (e_y + rate * ev_y) % 360
        e_z = (e_z + rate * ev_z) % 360

        #write transforms
        index = 16 * i

        r_y = np.radians(e_y)
        r_z = np.radians(e_z)
        c_y = np.cos(r_y)
        s_y = np.sin(r_y)
        c_z = np.cos(r_z)
        s_z = np.sin(r_z)

        transforms[index]      = c_y * c_z
        transforms[index + 1]  = c_y * s_z
        transforms[index + 2]  = -s_y
        transforms[index + 4]  = -s_z
        transforms[index + 5]  = c_z
        transforms[index + 8]  = s_y * c_z
        transforms[index + 9]  = s_y * s_z
        transforms[index + 10] = c_y
        transforms[index + 12] = x
        transforms[index + 13] = y
        transforms[index + 14] = z
        transforms[index + 15] = 1.0

        #write cube data back
        index = 9 * i
        cubes[index + 3] = e_x
        cubes[index + 4] = e_y
        cubes[index + 5] = e_z
        cubes[index + 6] = ev_x
        cubes[index + 7] = ev_y
        cubes[index + 8] = ev_z

@njit(cache = True)
def update_lights(
    lights: np.ndarray, transforms: np.ndarray, count: int) -> None:
    """
        Write the transform matrices to the given array.
        Lights don't have much updating to do.
    """

    for i in range(count):

        #unpack light data
        index = 7 * i
        x    = lights[index]
        y    = lights[index + 1]
        z    = lights[index + 2]

        #write transforms
        index = 16 * i

        transforms[index]      = 1.0
        transforms[index + 5]  = 1.0
        transforms[index + 10] = 1.0
        transforms[index + 12] = x
        transforms[index + 13] = y
        transforms[index + 14] = z
        transforms[index + 15] = 1.0

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
    __slots__ = ("entity_counts", "entities", "player")


    def __init__(self):
        """
            Initialize the scene.
        """

        self.entity_counts: dict[int, int] = {
            ENTITY_TYPE["CUBE"]: 0,
            ENTITY_TYPE["POINTLIGHT"]: 0
        }

        self.entities: dict[int, list[np.ndarray]] = {

            ENTITY_TYPE["CUBE"]: [
                np.zeros(200 * 9, dtype = np.float32),
                np.zeros(200 * 16, dtype = np.float32)
            ],
            ENTITY_TYPE["POINTLIGHT"]: [
                np.zeros(8 * 7, dtype = np.float32),
                np.zeros(8 * 16, dtype = np.float32),
                np.zeros(8 * 4, dtype = np.float32),
            ]
        }

        self._make_cubes()

        self._make_lights()

        self.player = Camera(
            position = [-10,0,0]
        )
    
    def _make_cubes(self) -> None:
        """
            Make the cubes!
        """

        for i in range(200):

            x = np.random.uniform(low = -10, high = 10)
            y = np.random.uniform(low = -10, high = 10)
            z = np.random.uniform(low = -10, high = 10)

            e_x = np.random.uniform(low = 0, high = 360)
            e_y = np.random.uniform(low = 0, high = 360)
            e_z = np.random.uniform(low = 0, high = 360)

            ev_x = np.random.uniform(low = -0.2, high = 0.2)
            ev_y = np.random.uniform(low = -0.2, high = 0.2)
            ev_z = np.random.uniform(low = -0.2, high = 0.2)

            index = 9 * i
            target_array = self.entities[ENTITY_TYPE["CUBE"]][0]

            target_array[index] = x
            target_array[index + 1] = y
            target_array[index + 2] = z
            target_array[index + 3] = e_x
            target_array[index + 4] = e_y
            target_array[index + 5] = e_z
            target_array[index + 6] = ev_x
            target_array[index + 7] = ev_y
            target_array[index + 8] = ev_z
        
        self.entity_counts[ENTITY_TYPE["CUBE"]] = 200

    def _make_lights(self) -> None:
        """
            Make the lights!
        """

        for i in range(8):

            x = np.random.uniform(low = -10, high = 10)
            y = np.random.uniform(low = -10, high = 10)
            z = np.random.uniform(low = -10, high = 10)

            r = np.random.uniform(low = 0.5, high = 1.0)
            g = np.random.uniform(low = 0.5, high = 1.0)
            b = np.random.uniform(low = 0.5, high = 1.0)

            s = np.random.uniform(low = 2, high = 5)

            index = 7 * i
            target_array = self.entities[ENTITY_TYPE["POINTLIGHT"]][0]

            target_array[index] = x
            target_array[index + 1] = y
            target_array[index + 2] = z
            target_array[index + 3] = r
            target_array[index + 4] = g
            target_array[index + 5] = b
            target_array[index + 6] = s

            index = 4 * i
            target_array = self.entities[ENTITY_TYPE["POINTLIGHT"]][2]

            target_array[index] = r
            target_array[index + 1] = g
            target_array[index + 2] = b
            target_array[index + 3] = 1.0
        
        self.entity_counts[ENTITY_TYPE["POINTLIGHT"]] = 8
    
    def update(self, dt: float) -> None:
        """
            Update all objects in the scene.

            Parameters:

                dt: framerate correction factor
        """

        update_cubes(
            cubes = self.entities[ENTITY_TYPE["CUBE"]][0],
            transforms = self.entities[ENTITY_TYPE["CUBE"]][1],
            count = self.entity_counts[ENTITY_TYPE["CUBE"]],
            rate = dt
        )

        update_lights(
            lights = self.entities[ENTITY_TYPE["POINTLIGHT"]][0],
            transforms = self.entities[ENTITY_TYPE["POINTLIGHT"]][1],
            count = self.entity_counts[ENTITY_TYPE["POINTLIGHT"]]
        )

        self.player.update()

    def move_player(self, d_pos: list[float]) -> None:
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
##################################### Control #################################
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
        self.renderer.register_entity(
            PIPELINE_TYPE["STANDARD"], ENTITY_TYPE["CUBE"])
        self.renderer.register_entity(
            PIPELINE_TYPE["EMISSIVE"], ENTITY_TYPE["POINTLIGHT"])

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
                self.scene.player, self.scene.entities, 
                self.scene.entity_counts)

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
##################################### View ####################################
#region
class GraphicsEngine:
    """
        Draws entities and stuff.
    """
    __slots__ = (
        "meshes", "materials", "shaders", 
        "model_buffers", "color_buffers", "entity_types")


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

        self.color_buffers: dict[int, Buffer] = {
            ENTITY_TYPE["POINTLIGHT"]: Buffer(size = 8, binding = 1)
        }
        
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
        

        for i in range(8):

            shader.cache_multi_location(
                UNIFORM_TYPE["LIGHT_COLOR"], f"lights[{i}].color")
            shader.cache_multi_location(
                UNIFORM_TYPE["LIGHT_POS"], f"lights[{i}].position")
            shader.cache_multi_location(
                UNIFORM_TYPE["LIGHT_STRENGTH"], f"lights[{i}].strength")
        
        shader = self.shaders[PIPELINE_TYPE["EMISSIVE"]]
        shader.use()

        shader.cache_single_location(UNIFORM_TYPE["VIEW"], "view")
        shader.cache_single_location(UNIFORM_TYPE["TINT"], "color")
    
    def register_entity(self, pipeline_type: int, entity_type: int) -> None:
        """
            Register an entity type to be rendered with the given pipeline.
        """

        if pipeline_type not in self.entity_types:
            return

        self.entity_types[pipeline_type].append(entity_type)
    
    def render(self, 
        camera: Camera, 
        renderables: dict[int, list[np.ndarray]],
        entity_counts: dict[int, int]) -> None:
        """
            Draw everything.

            Parameters:

                camera: the scene's camera

                renderables: all the entities to draw
            
        """

        self._prepare_frame(renderables)

        #refresh screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        view = camera.get_view_transform()

        shader = self.shaders[PIPELINE_TYPE["STANDARD"]]
        shader.use()

        glUniformMatrix4fv(
            shader.fetch_single_location(UNIFORM_TYPE["VIEW"]),
            1, GL_FALSE, view)
        glUniform3fv(
            shader.fetch_single_location(UNIFORM_TYPE["CAMERA_POS"]),
            1, camera.position)

        self._record_lights(
            shader, lights = renderables[ENTITY_TYPE["POINTLIGHT"]][0],
            count = entity_counts[ENTITY_TYPE["POINTLIGHT"]])
        
        for entity_type in renderables:

            if entity_type not in self.entity_types[PIPELINE_TYPE["STANDARD"]]:
                continue

            self.model_buffers[entity_type].read_from()
            self.materials[entity_type].use()
            self.meshes[entity_type].draw_instanced(
                0, entity_counts[entity_type])
        
        shader = self.shaders[PIPELINE_TYPE["EMISSIVE"]]
        shader.use()
        
        glUniformMatrix4fv(
            shader.fetch_single_location(UNIFORM_TYPE["VIEW"]),
            1, GL_FALSE, view)

        for entity_type in renderables:

            if entity_type not in self.entity_types[PIPELINE_TYPE["EMISSIVE"]]:
                continue

            self.model_buffers[entity_type].read_from()
            self.color_buffers[entity_type].read_from()
            self.meshes[entity_type].draw_instanced(
                0, entity_counts[entity_type])

        glFlush()
    
    def _prepare_frame(self, renderables: dict[int, list[Entity]]) -> None:
        """
            Update storage buffers based on scene data.
        """

        for entity_type, arrays in renderables.items():

            if entity_type not in self.model_buffers:
                continue
            self.model_buffers[entity_type].consume(arrays[1])
            
            if entity_type not in self.color_buffers:
                continue
            self.color_buffers[entity_type].consume(arrays[2])

    def _record_lights(self, 
        shader: int, lights: np.ndarray, count: int) -> None:
        """
            Record light data in the shader uniform.
        """

        for i in range(count):
            
            index = 7 * i
            
            pos      = lights[index : index + 3]
            color    = lights[index + 3 : index + 6]
            strength = lights[index + 6]

            glUniform3fv(
                shader.fetch_multi_location(UNIFORM_TYPE["LIGHT_POS"], i),
                1, pos)
            glUniform3fv(
                shader.fetch_multi_location(UNIFORM_TYPE["LIGHT_COLOR"], i),
                1, color)
            glUniform1f(
                shader.fetch_multi_location(UNIFORM_TYPE["LIGHT_STRENGTH"], i),
                strength)

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
        for buffer in self.color_buffers.values():
            buffer.destroy()

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
my_app = App()
my_app.run()
my_app.quit()