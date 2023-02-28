from config import *
import model
import view

class GameApp:

    def __init__(self):

        self.set_up_glfw()

        self.make_assets()

        self.set_up_input_systems()

        self.set_up_timer()
    
    def set_up_glfw(self) -> None:

        glfw.init()
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR,3
        )
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR,3
        )
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, 
            GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE
        )
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, 
            GLFW_CONSTANTS.GLFW_TRUE
        )
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_DOUBLEBUFFER, False
        )
        self.window = glfw.create_window(
            SCREEN_WIDTH, SCREEN_HEIGHT, 
            "Title", None, None
        )
        glfw.make_context_current(self.window)

    def make_assets(self) -> None:

        self.renderer = view.GameRenderer(self.window)

        self.scene = model.Scene()

        self.renderer.bake_geometry(
            self.scene.get_static_geometry()
        )
    
    def set_up_input_systems(self) -> None:

        glfw.set_input_mode(
            self.window, 
            GLFW_CONSTANTS.GLFW_CURSOR, 
            GLFW_CONSTANTS.GLFW_CURSOR_HIDDEN
        )

        self.space_down = glfw.get_key(
            self.window, GLFW_CONSTANTS.GLFW_KEY_SPACE
            ) == GLFW_CONSTANTS.GLFW_PRESS
        
        glfw.set_mouse_button_callback(
            self.window, self.handleMouseClick
        )

    def set_up_timer(self) -> None:
        """
            Set up the variables needed to measure the framerate
        """
        self.lastTime = glfw.get_time()
        self.currentTime = 0
        self.numFrames = 0
        self.frameTime = 0
    
    def mainLoop(self):

        result = RETURN_ACTION_CONTINUE
        while result == RETURN_ACTION_CONTINUE:
            #check events

            if glfw.window_should_close(self.window) \
                or glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_ESCAPE) == GLFW_CONSTANTS.GLFW_PRESS:
                result = RETURN_ACTION_EXIT
                break

            if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_SPACE) == GLFW_CONSTANTS.GLFW_PRESS:
                if not self.space_down:
                    self.space_pressed()
                self.space_down = True
            elif glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_SPACE) == GLFW_CONSTANTS.GLFW_RELEASE:
                self.space_down = False

            self.handleKeys()
            self.handleMouseMovement()

            glfw.poll_events()

            #update objects
            self.scene.update(self.frameTime / 16.6)

            #render
            self.renderer.render(self.scene)

            #timing
            self.showFrameRate()

        return result

    def handleKeys(self):

        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_W) == GLFW_CONSTANTS.GLFW_PRESS:
            self.scene.move_player(direction = 0, amount = 0.05*self.frameTime)
        elif glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_A) == GLFW_CONSTANTS.GLFW_PRESS:
            self.scene.move_player(direction = 90, amount = 0.05*self.frameTime)
        elif glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_S) == GLFW_CONSTANTS.GLFW_PRESS:
            self.scene.move_player(direction = 180, amount = 0.05*self.frameTime)
        elif glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_D) == GLFW_CONSTANTS.GLFW_PRESS:
            self.scene.move_player(direction = -90, amount = 0.05*self.frameTime)
        
        self.scene.set_spacebar_status(glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_SPACE) == GLFW_CONSTANTS.GLFW_PRESS)
    
    def space_pressed(self):

        direction = 0
        amount = 0

        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_W) == GLFW_CONSTANTS.GLFW_PRESS:
            amount = 1
        elif glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_A) == GLFW_CONSTANTS.GLFW_PRESS:
            direction = 90
            amount = 1
        elif glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_S) == GLFW_CONSTANTS.GLFW_PRESS:
            direction = 180
            amount = 1
        elif glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_D) == GLFW_CONSTANTS.GLFW_PRESS:
            direction = -90
            amount = 1

        self.scene.try_jump(direction, amount)
    
    def handleMouseMovement(self):

        
        (x,y) = glfw.get_cursor_pos(self.window)
        rate = self.frameTime / 16.6
        right_amount = -0.1 * rate * ((SCREEN_WIDTH / 2) - x)
        up_amount = -0.1 * rate * ((SCREEN_HEIGHT / 2) - y)
        self.scene.strafe_camera(right_amount, up_amount)
        
        glfw.set_cursor_pos(self.window, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    def handleMouseClick(self, window, button: int, action: int, mods: int) -> None:

        if action != GLFW_CONSTANTS.GLFW_PRESS:
            return
        
        if button == GLFW_CONSTANTS.GLFW_MOUSE_BUTTON_LEFT:
            self.scene.set_camera_zoom(10)
        elif button == GLFW_CONSTANTS.GLFW_MOUSE_BUTTON_RIGHT:
            self.scene.set_camera_zoom(5)
    
    def showFrameRate(self):

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
        
        self.renderer.destroy()