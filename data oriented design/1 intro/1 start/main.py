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
##################################### Model ###################################
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

    def update(self, dt: float) -> None:
        """
            Update the object, this is meant to be implemented by
            objects extending this class.

            Parameters:

                dt: framerate correction factor.
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


    def __init__(self, position: list[float], eulers: list[float],
        euler_velocity: list[float]):
        """
            Initialize the cube.

            Parameters:

                position: the position of the entity.

                eulers: the rotation of the entity
                        about each axis.
                
                euler_velocity: the angular velocity of the cube. 
        """

        super().__init__(position, eulers)
        self.euler_velocity = np.array(euler_velocity, dtype=np.float32)
    
    def update(self, dt: float) -> None:
        """
            Update the cube.

            Parameters:

                dt: framerate correction factor.

                camera_pos: the position of the camera in the scene
        """

        self.eulers = np.mod(self.eulers + dt * self.euler_velocity, 
            [360, 360, 360], dtype=np.float32)

class PointLight(Entity):
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

        super().__init__(position, eulers = [0,0,0])
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
        self.update(0)
    
    def update(self, dt: float) -> None:
        """
            Update the camera.

            Parameters:

                dt: framerate correction factor
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
    __slots__ = ("entities", "player", "lights")


    def __init__(self):
        """
            Initialize the scene.
        """

        self.entities: dict[int, list[Entity]] = {
            ENTITY_TYPE["CUBE"]: [
                Cube(
                    position = [
                        np.random.uniform(low = -10, high = 10) 
                        for _ in range(3)],
                    eulers = [
                        np.random.uniform(low = 0, high = 360) 
                        for _ in range(3)],
                    euler_velocity = [
                        np.random.uniform(low = -0.1, high = 0.1) 
                        for _ in range(3)]
                )

                for _ in range(200)
            ],
            ENTITY_TYPE["POINTLIGHT"]: [
                PointLight(
                    position = [np.random.uniform(low = -10, high = 10) for x in range(3)],
                    color = [np.random.uniform(low = 0.5, high = 1) for x in range(3)],
                    strength = 3
                )

                for _ in range(8)
            ]
        }

        self.player = Camera(
            position = [-10,0,0]
        )
    
    def update(self, dt: float) -> None:
        """
            Update all objects in the scene.

            Parameters:

                dt: framerate correction factor
        """

        for entities in self.entities.values():
            for entity in entities:
                entity.update(dt)

        self.player.update(dt)

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
                self.scene.player, self.scene.entities)

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
            ENTITY_TYPE["CUBE"]: Buffer(
                size = 1024, binding = 0, 
                element_count = 16, dtype = np.float32),
            ENTITY_TYPE["POINTLIGHT"]: Buffer(
                size = 8, binding = 0, 
                element_count = 16, dtype = np.float32)
        }

        self.color_buffers: dict[int, Buffer] = {
            ENTITY_TYPE["POINTLIGHT"]: Buffer(
                size = 8, binding = 1, 
                element_count = 4, dtype = np.float32)
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
        renderables: dict[int, list[Entity]]) -> None:
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

        for i,light in enumerate(renderables[ENTITY_TYPE["POINTLIGHT"]]):

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

            if entity_type not in self.entity_types[PIPELINE_TYPE["STANDARD"]]:
                continue

            self.model_buffers[entity_type].read_from()
            self.materials[entity_type].use()
            self.meshes[entity_type].draw_instanced(0, len(entities))
        
        shader = self.shaders[PIPELINE_TYPE["EMISSIVE"]]
        shader.use()
        
        glUniformMatrix4fv(
            shader.fetch_single_location(UNIFORM_TYPE["VIEW"]),
            1, GL_FALSE, view)

        for entity_type, entities in renderables.items():

            if entity_type not in self.entity_types[PIPELINE_TYPE["EMISSIVE"]]:
                continue

            self.model_buffers[entity_type].read_from()
            self.color_buffers[entity_type].read_from()
            self.meshes[entity_type].draw_instanced(0, len(entities))

        glFlush()
    
    def _prepare_frame(self, renderables: dict[int, list[Entity]]) -> None:
        """
            Update storage buffers based on scene data.
        """

        for entity_type, entities in renderables.items():

            if entity_type not in self.model_buffers:
                continue
            
            buffer = self.model_buffers[entity_type]
            for i, entity in enumerate(entities):
                model = entity.get_model_transform().reshape(16)
                buffer.record_element(i, model, padding = 0, default = 0.0)
            
            if entity_type not in self.color_buffers:
                continue
            
            buffer = self.color_buffers[entity_type]
            for i, entity in enumerate(entities):
                color = entity.color
                buffer.record_element(i, color, padding = 1, default = 1.0)

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
    __slots__ = (
        "size", "binding", "element_count", 
        "dtype", "host_memory", "device_memory", 
        "elements_updated")

    def __init__(self, size: int, binding: int, element_count: int, dtype: np.dtype):
        """
            Initialize the buffer.

            Parameters:

                size: number of entries on the buffer.

                binding: binding index

                element_count: number of elements per entry
        """

        self.size = size
        self.binding = binding
        self.element_count = element_count
        self.dtype = dtype

        self.host_memory = np.zeros(element_count * size, dtype=dtype)

        self.device_memory = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.device_memory)
        glBufferStorage(
            GL_SHADER_STORAGE_BUFFER, self.host_memory.nbytes, 
            self.host_memory, GL_DYNAMIC_STORAGE_BIT)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, binding, self.device_memory)
        self.elements_updated = 0
    
    def record_element(self, i: int, element: np.ndarray, padding: int, default: any) -> None:
        """
            Record the given element in position i, if this exceeds the buffer size,
            the buffer is resized.
        """

        if i >= self.size:
            self.resize()

        index = self.element_count * i
        elements_to_write = self.element_count - padding
        a = index + elements_to_write
        b = index + self.element_count
        self.host_memory[index : a] = element[:]
        self.host_memory[a : b] = default

        self.elements_updated += 1
    
    def resize(self) -> None:
        """
            Resize the buffer, uses doubling strategy.
        """

        self.destroy()

        new_size = self.size * 2

        host_memory = np.zeros(self.element_count * new_size, dtype=self.dtype)
        host_memory[0:self.element_count * self.size] = self.host_memory[:]
        self.host_memory = host_memory
        self.size = new_size

        self.device_memory = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.device_memory)
        glBufferStorage(
            GL_SHADER_STORAGE_BUFFER, self.host_memory.nbytes, 
            self.host_memory, GL_DYNAMIC_STORAGE_BIT)

    def read_from(self) -> None:
        """
            Upload the CPU data to the buffer, then arm it for reading.
        """

        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.device_memory)
        glBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, self.element_count * 4 * self.elements_updated, self.host_memory)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, self.binding, self.device_memory)
        self.elements_updated = 0
    
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
            Material2D(f"gfx/{filename}_albedo.{filetype}", 0),
            Material2D(f"gfx/{filename}_ao.{filetype}", 1),
            Material2D(f"gfx/{filename}_normal.{filetype}", 2),
            Material2D(f"gfx/{filename}_specular.{filetype}", 3),
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