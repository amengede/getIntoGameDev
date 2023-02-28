import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr

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

class Entity:
    """ Represents a general object with a position and rotation applied"""


    def __init__(self, position: list[float], eulers: list[float]):
        """
            Initialize the entity, store its state and update its transform.

            Parameters:

                position: The position of the entity in the world (x,y,z)

                eulers: Angles (in degrees) representing rotations around the x,y,z axes.
        """

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)
    
    def get_model_transform(self) -> np.ndarray:
        """
            Calculates and returns the entity's transform matrix,
            based on its position and rotation.
        """

        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        
        model_transform = pyrr.matrix44.multiply(
            m1=model_transform, 
            m2=pyrr.matrix44.create_from_z_rotation(
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

    def update(self, rate: float) -> None:

        raise NotImplementedError
    
class Triangle(Entity):
    """ A triangle that spins. """

    def __init__(
        self, position: list[float], 
        eulers: list[float], scale: list[float]):
        """ Initialize a triangle with the given scale."""

        super().__init__(position, eulers)
        self.scale = np.array(scale, dtype = np.float32)
    
    def update(self, rate: float) -> None:
        """
            Update the triangle.

            Parameters:

                rate: framerate correction factor
        """

        pass
    
    def get_model_transform(self) -> np.ndarray:

        return pyrr.matrix44.multiply(
            m1 =  pyrr.matrix44.create_from_scale(
                scale = self.scale,
                dtype = np.float32
            ),
            m2 = super().get_model_transform()
        )

class Player(Triangle):
    """ A player character """


    def __init__(self, position, eulers, scale):
        """ Initialise a player character. """
        
        super().__init__(position, eulers, scale)
        self.camera = None
    
    def update(self, target: Triangle, rate: float) -> None:
        """
            Update the player.

            Parameters:

                target: the triangle to move towards.

                rate: framerate correction factor
        """

        if target is not None:
            self.move_towards(target.position, 0.1 * rate)

    def move_towards(self, targetPosition: np.ndarray, amount: float) -> None:
        """
            Move towards the given point by the given amount.
        """
        directionVector = targetPosition - self.position
        angle = np.arctan2(-directionVector[1],directionVector[0])
        self.move(angle, amount)
    
    def move(self, direction: float, amount: float) -> None:
        """
            Move by the given amount in the given direction (in radians).
        """
        self.position[0] += amount * np.cos(direction, dtype=np.float32)
        self.position[1] -= amount * np.sin(direction, dtype=np.float32)
        self.camera.position[0] += amount * np.cos(direction, dtype=np.float32)
        self.camera.position[1] -= amount * np.sin(direction, dtype=np.float32)
        self.eulers[2] = np.degrees(direction) - 45

class Camera(Entity):
    """ A third person camera controller. """

    def __init__(self, position):

        super().__init__(position, eulers = [0,0,0])

        self.forwards = np.array([0, 0, 0],dtype=np.float32)
        self.right = np.array([0, 0, 0],dtype=np.float32)
        self.up = np.array([0, 0, 0],dtype=np.float32)

        self.localUp = np.array([0, 0, 1], dtype=np.float32)
        self.targetObject: Entity = None

    def update(self) -> None:
        """ Updates the camera """

        self.calculate_vectors_cross_product()
    
    def calculate_vectors_cross_product(self) -> None:
        """ 
            Calculate the camera's fundamental vectors.

            There are various ways to do this, this function
            achieves it by using cross products to produce
            an orthonormal basis.
        """
        
        #TODO: set the camera's forwards vector so it's always looking towards its
        #       target object.
        self.forwards = None
        self.right = pyrr.vector.normalize(pyrr.vector3.cross(self.forwards, self.localUp))
        self.up = pyrr.vector.normalize(pyrr.vector3.cross(self.right, self.forwards))

    def get_view_transform(self) -> np.ndarray:
        """ Return's the camera's view transform. """

        #TODO: return a look_at vector from the camera
        #       towards its target object
        return None

class Scene:
    """ 
        Manages all logical objects in the game,
        and their interactions.
    """

    def __init__(self):

        self.player = Player(
            position = [0,1,0],
            eulers = [0,0,0],
            scale = [1,1,1]
        )
        self.camera = Camera(position = [-3,1,3])
        self.player.camera = self.camera
        self.camera.targetObject = self.player

        self.click_dots: list[Entity] = []

        #make row of triangles
        self.triangles: list[Entity] = []
        for x in range(1,16,3):
            self.triangles.append(
                Triangle(
                    position = [x,1,0.5],
                    eulers = [0,0,0],
                    scale = [0.5, 0.5, 0.5],
                )
            )
    
    def update(self, rate: float) -> None:
        """ 
            Update all objects managed by the scene.

            Parameters:

                rate: framerate correction factor
        """

        for triangle in self.triangles:
            triangle.update(rate)
        for dot in self.click_dots:
            dot.update(rate)
        targetDot = None
        if len(self.click_dots) > 0:
            targetDot = self.click_dots[0]
        self.player.update(targetDot, rate)
        self.camera.update()

        #check if dot can be deleted
        if targetDot is not None:
            if pyrr.vector.length(targetDot.position - self.player.position) < 0.1:
                self.click_dots.pop(self.click_dots.index(targetDot))
    
    def lay_down_dot(self, position: list[float]) -> None:
        """ Drop a dot at the given position """

        self.click_dots.append(
            Triangle(
                position = position,
                eulers = [0,0,0],
                scale = [0.1, 0.1, 0.1],
            )
        )
    
    def move_camera(self, dPos: np.ndarray) -> None:
        """
            Move the camera by the given amount in its fundamental vectors.
        """

        #TODO: shift the camera's position, use the components of dPos
        #       as coefficients for a linear combination of the
        #       camera's direction vectors
        pass

class App:
    """ The main program """


    def __init__(self):
        """ Set up the program """
        
        self.set_up_glfw()
        
        self.make_assets()
        
        self.set_onetime_uniforms()

        self.get_uniform_locations()

        self.set_up_input_systems()

        self.set_up_timer()

        self.mainLoop()
    
    def set_up_glfw(self) -> None:
        """ Set up the glfw environment """

        self.screenWidth = 640
        self.screenHeight = 480

        glfw.init()
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR,3)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR,3)
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, 
            GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE
        )
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, 
            GLFW_CONSTANTS.GLFW_TRUE
        )
        glfw.window_hint(GLFW_CONSTANTS.GLFW_DOUBLEBUFFER, False)
        self.window = glfw.create_window(
            self.screenWidth, self.screenHeight, "Title", None, None
        )
        glfw.make_context_current(self.window)

    def make_assets(self) -> None:
        """ Make any assets used by the App"""

        self.scene = Scene()
        self.triangle_mesh = TriangleMesh()
        self.shader = createShader("shaders/vertex.txt", "shaders/fragment.txt")
    
    def set_onetime_uniforms(self) -> None:
        """ Set any uniforms which can simply get set once and forgotten """

        glUseProgram(self.shader)

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, 
            aspect = self.screenWidth / self.screenHeight, 
            near = 0.1, far = 10, dtype = np.float32
        )
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader, "projection"), 
            1, GL_FALSE, projection_transform
        )
    
    def get_uniform_locations(self) -> None:
        """ Query and store the locations of any uniforms on the shader """

        glUseProgram(self.shader)
        self.modelMatrixLocation = glGetUniformLocation(self.shader,"model")
        self.viewMatrixLocation = glGetUniformLocation(self.shader, "view")
    
    def set_up_input_systems(self) -> None:

        glfw.set_mouse_button_callback(self.window, self.handleMouse)
    
    def set_up_timer(self) -> None:
        """
            Set up the variables needed to measure the framerate
        """
        self.lastTime = glfw.get_time()
        self.currentTime = 0
        self.numFrames = 0
        self.frameTime = 0
    
    def mainLoop(self):

        glClearColor(0.1, 0.2, 0.2, 1)
        (w,h) = glfw.get_framebuffer_size(self.window)
        glViewport(0,0,w, h)
        glEnable(GL_DEPTH_TEST)
        running = True

        while (running):

            #check events
            if glfw.window_should_close(self.window) \
                or glfw.get_key(
                    self.window, GLFW_CONSTANTS.GLFW_KEY_ESCAPE
                ) == GLFW_CONSTANTS.GLFW_PRESS:
                running = False
            
            self.handleKeys()
            
            glfw.poll_events()

            #update scene
            self.scene.update(self.frameTime / 16.667)
            
            #refresh screen
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glUseProgram(self.shader)

            glUniformMatrix4fv(
                self.viewMatrixLocation, 1, GL_FALSE, 
                self.scene.camera.get_view_transform()
            )

            glUniformMatrix4fv(
                self.modelMatrixLocation,
                1,GL_FALSE,
                self.scene.player.get_model_transform()
            )
            glBindVertexArray(self.triangle_mesh.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.triangle_mesh.vertex_count)

            for triangle in self.scene.triangles:
                glUniformMatrix4fv(
                    self.modelMatrixLocation,
                    1,GL_FALSE,
                    triangle.get_model_transform()
                )
                glDrawArrays(GL_TRIANGLES, 0, self.triangle_mesh.vertex_count)
            
            for dot in self.scene.click_dots:
                glUniformMatrix4fv(
                    self.modelMatrixLocation,
                    1,GL_FALSE,
                    dot.get_model_transform()
                )
                glDrawArrays(GL_TRIANGLES, 0, self.triangle_mesh.vertex_count)

            glFlush()

            #timing
            self.calculateFramerate()
        self.quit()
    
    def handleKeys(self) -> None:
        """ Handle keys. """

        camera_movement = [0,0,0]

        if glfw.get_key(
            self.window, GLFW_CONSTANTS.GLFW_KEY_W
            ) == GLFW_CONSTANTS.GLFW_PRESS:
            camera_movement[2] += 1
        elif glfw.get_key(
            self.window, GLFW_CONSTANTS.GLFW_KEY_A
            ) == GLFW_CONSTANTS.GLFW_PRESS:
            camera_movement[1] -= 1
        elif glfw.get_key(
            self.window, GLFW_CONSTANTS.GLFW_KEY_S
            ) == GLFW_CONSTANTS.GLFW_PRESS:
            camera_movement[2] -= 1
        elif glfw.get_key(
            self.window, GLFW_CONSTANTS.GLFW_KEY_D
            ) == GLFW_CONSTANTS.GLFW_PRESS:
            camera_movement[1] += 1
            
        dPos = 0.1 * self.frameTime / 16.667 * np.array(
            camera_movement,
            dtype = np.float32
        )

        self.scene.move_camera(dPos)
    
    def handleMouse(self, window, button: int, action: int, mods: int) -> None:

        if button != GLFW_CONSTANTS.GLFW_MOUSE_BUTTON_LEFT \
            or action != GLFW_CONSTANTS.GLFW_PRESS:
            return
        
        #fetch camera's vectors
        forward = self.scene.camera.forwards
        up = self.scene.camera.up
        right = self.scene.camera.right

        #get mouse's displacement from screen center
        (x,y) = glfw.get_cursor_pos(self.window)
        rightAmount = (x - self.screenWidth//2)/self.screenWidth
        upAmount = (self.screenHeight//2 - y)/self.screenWidth

        #TODO: get the resultant vector by a linear combination of the camera's vectors.
        resultant = None

        #trace from camera's position until we hit the ground
        if (resultant[2] < 0):
            #TODO: grab a copy of the camera's position
            x = None
            y = None
            z = None
            while (z > 0):
                #TODO: step forward by the resultant vector
                pass
            self.scene.lay_down_dot(
                position = [x,y,0]
            )
    
    def calculateFramerate(self) -> None:
        """
            Calculate the framerate and frametime
        """

        self.currentTime = glfw.get_time()
        delta = self.currentTime - self.lastTime
        if (delta >= 1):
            framerate = int(self.numFrames/delta)
            glfw.set_window_title(self.window, f"Running at {framerate} fps.")
            self.lastTime = self.currentTime
            self.numFrames = -1
            self.frameTime = float(1000.0 / max(60,framerate))
        self.numFrames += 1
    
    def quit(self):
        self.triangle_mesh.destroy()
        glDeleteProgram(self.shader)
        glfw.terminate()

class TriangleMesh:


    def __init__(self):

        # x, y, z, r, g, b
        self.vertices = (
            -0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
             0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
             0.0,  0.5, 0.0, 0.0, 0.0, 1.0
        )
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vertex_count = 3

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    def destroy(self):
        
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))

myApp = App()