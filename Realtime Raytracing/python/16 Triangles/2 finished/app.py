from config import *
import engine
import scene

class App:
    """
        Calls high level control functions (handle input, draw scene etc)
    """

    def __init__(self):

        self.screenWidth = 800
        self.screenHeight = 600

        self.set_up_glfw()

        self.make_assets()

        self.set_up_input_systems()

        self.set_up_timer()

        self.mainLoop()
    
    def set_up_glfw(self) -> None:
        """
            Set up glfw.
        """

        glfw.init()
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR,4)
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
        """
            Make everything needed by the program.
        """

        self.scene = scene.Scene()
        self.graphicsEngine = engine.Engine(self.screenWidth, self.screenHeight, self.scene)
    
    def set_up_input_systems(self) -> None:
        """
            configure the mouse and keyboard
        """

        glfw.set_input_mode(
            self.window, 
            GLFW_CONSTANTS.GLFW_CURSOR, 
            GLFW_CONSTANTS.GLFW_CURSOR_HIDDEN
        )
        glfw.set_cursor_pos(
            self.window,
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

    def set_up_timer(self) -> None:
        """
            Set up the framerate timer
        """

        self.lastTime = glfw.get_time()
        self.currentTime = glfw.get_time()
        self.numFrames = 0
        self.frameTime = 0
        self.lightCount = 0

    def mainLoop(self) -> None:
        """
            Run the main program
        """

        running = True
        while (running):
            #events
            if glfw.window_should_close(self.window) \
                or glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_ESCAPE) == GLFW_CONSTANTS.GLFW_PRESS:
                running = False
            
            self.handleKeys()
            self.handleMouse()

            glfw.poll_events()
            
            #render
            self.graphicsEngine.renderScene(self.scene)

            #timing
            self.calculateFramerate()
        self.quit()
    
    def handleKeys(self) -> None:
        """
            handle the current key state
        """

        rate = self.frameTime / 16
        combo = 0

        if glfw.get_key(
            self.window, GLFW_CONSTANTS.GLFW_KEY_W
            ) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 1
        if glfw.get_key(
            self.window, GLFW_CONSTANTS.GLFW_KEY_A
            ) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 2
        if glfw.get_key(
            self.window, GLFW_CONSTANTS.GLFW_KEY_S
            ) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 4
        if glfw.get_key(
            self.window, GLFW_CONSTANTS.GLFW_KEY_D
            ) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 8
        
        if combo in self.walk_offset_lookup:
            angle = np.radians(self.walk_offset_lookup[combo])
            dx =  0.1 * rate * np.cos(angle)
            dy = -0.1 * rate * np.sin(angle)
            self.scene.move_player(dx, dy)
    
    def handleMouse(self) -> None:
        """
            Handle mouse movement.
        """

        (x,y) = glfw.get_cursor_pos(self.window)
        theta_increment = 0.05 * ((self.screenWidth / 2.0) - x)
        phi_increment = 0.05 * ((self.screenHeight / 2.0) - y)
        
        self.scene.spin_player([theta_increment, phi_increment])
        glfw.set_cursor_pos(self.window, self.screenWidth // 2, self.screenHeight // 2)
    
    def calculateFramerate(self) -> None:
        """
            Calculate the framerate of the program.
        """

        self.currentTime = glfw.get_time()
        delta = self.currentTime - self.lastTime
        if (delta >= 1):
            framerate = int(self.graphicsEngine.numFrames/delta)
            glfw.set_window_title(self.window, f"Running at {framerate} fps.")
            self.lastTime = self.currentTime
            self.graphicsEngine.numFrames = 0
            self.frameTime = float(1000.0 / max(60,framerate))
            self.graphicsEngine.adaptResolution(framerate)
        self.graphicsEngine.numFrames += 1

    def quit(self) -> None:
        """
            For some reason, the graphics engine's destructor throws weird errors.
        """
        
        #self.graphicsEngine.destroy()
        glfw.terminate()