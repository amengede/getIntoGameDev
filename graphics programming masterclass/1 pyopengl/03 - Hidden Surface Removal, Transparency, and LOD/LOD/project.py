import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr

################### Constants        ########################################

OBJECT_MONKEY = 0
OBJECT_CAMERA = 1

################### Helper Functions ########################################

def createShader(vertexFilepath: str, fragmentFilepath: str) -> int:
    """
        Compile and link a shader program from source.

        Parameters:

            vertexFilepath: filepath to the vertex shader source code (relative to this file)

            fragmentFilepath: filepath to the fragment shader source code (relative to this file)
        
        Returns:

            An integer, being a handle to the shader location on the graphics card
    """

    with open(vertexFilepath,'r') as f:
        vertex_src = f.readlines()

    with open(fragmentFilepath,'r') as f:
        fragment_src = f.readlines()
    
    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                            compileShader(fragment_src, GL_FRAGMENT_SHADER))
    
    return shader

################### Model ###################################################

class Entity:
    """ Represents a general object with a position and rotation applied"""


    def __init__(
        self, position: list[float], 
        eulers: list[float], objectType: int,
        color: list[float] = None):
        """
            Initialize the entity, store its state and update its transform.

            Parameters:

                position: The position of the entity in the world (x,y,z)

                eulers: Angles (in degrees) representing rotations around the x,y,z axes.

                objectType: The type of object which the entity represents,
                            this should match a named constant.
                
                color: The RGBA color of the entity

        """

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)
        self.objectType = objectType
        self.color = None
        if color is not None:
            self.color = np.array(color, dtype = np.float32)
    
    def get_model_transform(self) -> np.ndarray:
        """
            Calculates and returns the entity's transform matrix,
            based on its position and rotation.
        """

        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        
        model_transform = pyrr.matrix44.multiply(
            m1=model_transform, 
            m2=pyrr.matrix44.create_from_y_rotation(
                theta = np.radians(self.eulers[2]), 
                dtype=np.float32
            )
        )

        model_transform = pyrr.matrix44.multiply(
            m1=model_transform, 
            m2=pyrr.matrix44.create_from_translation(
                vec=self.position,
                dtype=np.float32
            )
        )

        return model_transform

    def get_color(self) -> np.ndarray:
        """ Get the entity's color """

        return self.color
    
    def update(self) -> None:

        raise NotImplementedError

class Monkey(Entity):
    """ Who let that monkey out of the zoo? """

    def __init__(
        self, position: list[float], 
        eulers: list[float], color: list[float]):

        super().__init__(position, eulers, OBJECT_MONKEY, color)
    
    def update(self) -> None:
        """
            Update the quad
        """

        pass

class Camera(Entity):
    """ A first person camera controller. """


    def __init__(self, position: list[float], eulers: list[float]):

        super().__init__(position, eulers, OBJECT_CAMERA)

        self.localUp = np.array([0,0,1], dtype=np.float32)

        #directions after rotation
        self.up = np.array([0,0,1], dtype=np.float32)
        self.right = np.array([0,1,0], dtype=np.float32)
        self.forwards = np.array([1,0,0], dtype=np.float32)
    
    def calculate_vectors(self) -> None:
        """ 
            Calculate the camera's fundamental vectors.

            There are various ways to do this, this function
            achieves it by using cross products to produce
            an orthonormal basis.
        """

        #calculate the forwards vector directly using spherical coordinates
        self.forwards = np.array(
            [
                np.cos(np.radians(self.eulers[2])) * np.cos(np.radians(self.eulers[1])),
                np.sin(np.radians(self.eulers[2])) * np.cos(np.radians(self.eulers[1])),
                np.sin(np.radians(self.eulers[1]))
            ],
            dtype=np.float32
        )
        self.right = pyrr.vector.normalise(np.cross(self.forwards, self.localUp))
        self.up = pyrr.vector.normalise(np.cross(self.right, self.forwards))
        
    def update(self) -> None:
        """ Updates the camera """

        self.calculate_vectors()
    
    def get_view_transform(self) -> np.ndarray:
        """ Return's the camera's view transform. """

        return pyrr.matrix44.create_look_at(
            eye = self.position,
            target = self.position + self.forwards,
            up = self.up,
            dtype = np.float32
        )
        
class Scene:
    """ 
        Manages all logical objects in the game,
        and their interactions.
    """


    def __init__(self):
        """ Create a scene """

        self.renderables: dict[int, list[Entity]] = {}
        self.renderables[OBJECT_MONKEY] = [
            Monkey(
                position = [3,0,0],
                eulers = [0,0,0],
                color = [1,0,0,1.0]
            ),
        ]

        self.camera = Camera(
            position = [0,0,0],
            eulers = [0,0,0]
        )
    
    def update(self) -> None:
        """ 
            Update all objects managed by the scene.
        """

        for _,objectList in self.renderables.items():
            for object in objectList:
                object.update()
        
        self.camera.update()
    
    def move_camera(self, dPos: np.ndarray) -> None:
        """ Moves the camera by the given amount """

        self.camera.position += dPos
    
    def spin_camera(self, dEulers: np.ndarray) -> None:
        """ 
            Change the camera's euler angles by the given amount,
            performing appropriate bounds checks.
        """

        self.camera.eulers += dEulers

        if self.camera.eulers[2] < 0:
            self.camera.eulers[2] += 360
        elif self.camera.eulers[2] > 360:
            self.camera.eulers[2] -= 360
        
        self.camera.eulers[1] = min(89, max(-89, self.camera.eulers[1]))

################### View  #####################################################

class Mesh:
    """ A general mesh """


    def __init__(self):

        self.vertex_count = 0

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
    
    def destroy(self):
        
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))

class ObjMesh(Mesh):
    """ A mesh which can be loaded from an obj file. """


    def __init__(self, filename):
        """ Load the given file, create a buffer and upload to it. """

        super().__init__()
        vertices = self.loadMesh(filename)
        self.vertex_count = len(vertices)//3
        vertices = np.array(vertices, dtype=np.float32)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
    
    def loadMesh(self, filename) -> list[float]:

        v: list[list[float]] = []
        vertices: list[float] = []

        #open the obj file and read the data
        with open(filename,'r') as f:
            line = f.readline()
            while line:
                
                words = line.split(" ")
                if words[0]=="v":
                    v.append(self.read_vertex_data(words))
                elif words[0]=="f":
                    self.read_face_data(words, v, vertices)
                line = f.readline()
        
        return vertices
    
    def read_vertex_data(self, words: list[str]) -> list[float]:
        """ Append the given vertex description to the vertex set."""
        
        return [float(words[1]), float(words[2]), float(words[3])]
    
    def read_face_data(
        self, words: list[str], 
        v: list[list[float]], vertices: list[float]) -> None:
        
        # obj file uses triangle fan format for each face individually.
        triangleCount = len(words) - 3
        for i in range(triangleCount):
            self.read_corner(words[1], v, vertices)
            self.read_corner(words[i+2], v, vertices)
            self.read_corner(words[i+3], v, vertices)
    
    def read_corner(
        self, description: str,
        v: list[list[float]], vertices: list[float]) -> None:

        v_vt_vn = description.split("/")
        for element in v[int(v_vt_vn[0]) - 1]:
            vertices.append(element)

class Renderer:


    def __init__(self, screenWidth: int, screenHeight: int):

        self.screenWidth = screenWidth
        self.screenHeight = screenHeight

        self.set_up_opengl()

        self.make_assets()

        self.set_onetime_uniforms()

        self.get_uniform_locations()
    
    def set_up_opengl(self) -> None:
        """
            Set up any general options used in OpenGL rendering.
        """

        glClearColor(0.0, 0.0, 0.0, 1)

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    def make_assets(self):
        """
            Load/Create assets (eg. meshes and materials) that the renderer will use.
        """

        self.meshes: dict[int, list[Mesh]] = {
            OBJECT_MONKEY: [
                ObjMesh(f"models/monkey_{level}.obj") 
                for level in ["a","b","c","d","e","f","g","h","i","j","k"]
            ],
        }

        self.shader = createShader("shaders/vertex.txt", "shaders/fragment.txt")
    
    def set_onetime_uniforms(self):
        """ Set any uniforms which can simply get set once and forgotten """
        
        glUseProgram(self.shader)
        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = self.screenWidth / self.screenHeight, 
            near = 0.5, far = 100, dtype = np.float32
        )
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader, "projection"), 
            1, GL_FALSE, projection_transform
        )

    def get_uniform_locations(self):
        """ Query and store the locations of any uniforms on the shader """

        glUseProgram(self.shader)
        self.modelMatrixLocation = glGetUniformLocation(self.shader,"model")
        self.viewMatrixLocation = glGetUniformLocation(self.shader, "view")
        self.objectColorLocation = glGetUniformLocation(self.shader, "objectColor")

    def get_level(self, dist: float) -> int:
        """
        a:  0+ :  0
        b: 10+ :  1
        c: 20+ :  2
        d: 30+ :  3
        e: 40+ :  4
        f: 50+ :  5
        h: 60+ :  6
        i: 70+ :  7
        j: 80+ :  8
        k: 90+ :  9
        """

        if dist > 90:
            return 9
        if dist > 80:
            return 8
        if dist > 70:
            return 7
        if dist > 60:
            return 6
        if dist > 50:
            return 5
        if dist > 40:
            return 4
        if dist > 30:
            return 3
        if dist > 20:
            return 2
        if dist > 10:
            return 1
        return 0
    
    def render(
        self, camera: Camera, 
        renderables: dict[int, list[Entity]]) -> None:
        """
            Render a frame.

            Parameters:

                camera: the camera to render from

                renderables: a dictionary of entities to draw, keys are the
                            entity types, for each of these there is a list
                            of entities.
        """

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shader)

        glUniformMatrix4fv(
            self.viewMatrixLocation, 
            1, GL_FALSE, camera.get_view_transform()
        )

        for objectType,objectList in renderables.items():
            
            for object in objectList:
                level = self.get_level(
                    dist = pyrr.vector.length(camera.position - object.position)
                )
                mesh = self.meshes[objectType][level]
                glBindVertexArray(mesh.vao)
                glUniformMatrix4fv(
                    self.modelMatrixLocation,
                    1,GL_FALSE,
                    object.get_model_transform()
                )
                glUniform4fv(
                    self.objectColorLocation,
                    1, object.get_color()
                )
                glDrawArrays(GL_LINES, 0, mesh.vertex_count)

        pg.display.flip()
    
    def destroy(self):
        for (_,meshGroup) in self.meshes.items():
            for mesh in meshGroup:
                mesh.destroy()
        glDeleteProgram(self.shader)
        pg.quit()

################### Control ###################################################

class App:
    """ The main program """


    def __init__(self):
        """ Set up the program """

        self.set_up_pygame()

        self.make_objects()

        self.set_up_input_systems()

        self.mainLoop()
    
    def set_up_pygame(self) -> None:
        """ Set up the pygame environment """
        self.screenWidth = 640
        self.screenHeight = 480
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode(
            (self.screenWidth, self.screenHeight), 
            pg.OPENGL|pg.DOUBLEBUF
        )
        self.clock = pg.time.Clock()

    def make_objects(self) -> None:
        """ Make any object used by the App"""

        self.renderer = Renderer(self.screenWidth, self.screenHeight)
        self.scene = Scene()
    
    def set_up_input_systems(self) -> None:
        """ Run any mouse/keyboard configuration here. """

        pg.mouse.set_visible(False)
        pg.mouse.set_pos(
            self.screenWidth // 2, 
            self.screenHeight // 2
        )

        self.walk_offset_lookup = {
            1: 0,
            2: 90,
            3: 45,
            4: 180,
            6: 135,
            7: 90,
            8: 270,
            9: 315,
            11: 0,
            12: 225,
            13: 270,
            14: 180
        }

    def mainLoop(self):
        """ Run the App """

        running = True
        while (running):
            #check events
            for event in pg.event.get():
                if (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    running = False
                if (event.type == pg.QUIT):
                    running = False
            
            self.handleKeys()
            self.handleMouse()
            
            #update scene
            self.scene.update()

            #render
            self.renderer.render(
                camera = self.scene.camera,
                renderables = self.scene.renderables
            )

            #timing
            self.clock.tick(60)

        self.quit()
    
    def handleKeys(self) -> None:
        """
            Handle keys.
        """

        combo = 0
        directionModifier = 0

        keys = pg.key.get_pressed()

        if keys[pg.K_w]:
            combo += 1
        if keys[pg.K_a]:
            combo += 2
        if keys[pg.K_s]:
            combo += 4
        if keys[pg.K_d]:
            combo += 8
        
        if combo in self.walk_offset_lookup:

            directionModifier = self.walk_offset_lookup[combo]
            
            dPos = 0.1 * np.array(
                [
                    np.cos(np.deg2rad(self.scene.camera.eulers[2] + directionModifier)),
                    np.sin(np.deg2rad(self.scene.camera.eulers[2] + directionModifier)),
                    0
                ],
                dtype = np.float32
            )

            self.scene.move_camera(dPos)

    def handleMouse(self) -> None:
        """
            Handle mouse movement.
        """

        (x,y) = pg.mouse.get_pos()
        theta_increment = (self.screenWidth / 2.0) - x
        phi_increment = (self.screenHeight / 2.0) - y
        dEulers = np.array([0, phi_increment, theta_increment], dtype=np.float32)
        self.scene.spin_camera(dEulers)
        pg.mouse.set_pos(self.screenWidth // 2, self.screenHeight // 2)
    
    def quit(self):
        self.renderer.destroy()

myApp = App()