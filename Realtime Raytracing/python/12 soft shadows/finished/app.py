from config import *
import engine
import scene

class App:
    """
        Calls high level control functions (handle input, draw scene etc)
    """

    def __init__(self):

        glfw.init()
        self.screenWidth = 800
        self.screenHeight = 600
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_DOUBLEBUFFER, False)
        self.window = glfw.create_window(self.screenWidth, self.screenHeight, "Something", None, None)
        glfw.make_context_current(self.window)
        glfw.set_input_mode(self.window, GLFW_CONSTANTS.GLFW_CURSOR, GLFW_CONSTANTS.GLFW_CURSOR_HIDDEN)

        self.graphicsEngine = engine.Engine(self.screenWidth, self.screenHeight, self.window)
        self.scene = scene.Scene()

        self.lastTime = glfw.get_time()
        self.currentTime = 0
        self.numFrames = 0
        self.frameTime = 0

        self.mainLoop()
    
    def mainLoop(self):

        running = True
        while (running):
            #events
            if glfw.window_should_close(self.window)\
                or glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_ESCAPE) == GLFW_CONSTANTS.GLFW_PRESS:
                    running = False
            self.handleKeys()
            self.handleMouse()
            glfw.poll_events()
            self.scene.update(rate = self.frameTime / 16)
            
            #render
            self.graphicsEngine.renderScene(self.scene)

            #timing
            self.calculateFramerate()
        self.quit()
    
    def handleKeys(self):
        """
            handle the current key state
        """

        rate = self.frameTime / 16

        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_W) == GLFW_CONSTANTS.GLFW_PRESS:
            self.scene.move_player(0.1 * rate, 0)
        elif glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_A) == GLFW_CONSTANTS.GLFW_PRESS:
            self.scene.move_player(0, -0.1 * rate)
        elif glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_S) == GLFW_CONSTANTS.GLFW_PRESS:
            self.scene.move_player(-0.1 * rate, 0)
        elif glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_D) == GLFW_CONSTANTS.GLFW_PRESS:
            self.scene.move_player(0, 0.1 * rate)
    
    def handleMouse(self):

        (x,y) = glfw.get_cursor_pos(self.window)
        theta_increment = self.frameTime * 0.05 * ((self.screenWidth // 2) - x)
        phi_increment = self.frameTime * 0.05 * ((self.screenHeight // 2) - y)
        self.scene.spin_player((theta_increment, phi_increment))
        glfw.set_cursor_pos(self.window, self.screenWidth // 2,self.screenHeight // 2)
    
    def calculateFramerate(self):

        self.currentTime = glfw.get_time()
        delta = self.currentTime - self.lastTime
        if (delta >= 1):
            framerate = max(1,int(self.numFrames/delta))
            glfw.set_window_title(self.window, f"Running at {framerate} fps.")
            self.lastTime = self.currentTime
            self.numFrames = -1
            self.frameTime = float(1000.0 / max(1,framerate))
        self.numFrames += 1

    def quit(self):
        #self.graphicsEngine.destroy()
        pass