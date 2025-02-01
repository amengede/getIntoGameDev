from config import *
import model
import view

class GameApp:

    def __init__(self, window):

        self.window = window

        self.renderer = view.GameRenderer(window)

        self.scene = model.Scene()

        self.renderer.bake_geometry(
            self.scene.get_static_geometry(), 
            self.scene.ground
        )

        glfw.set_input_mode(self.window, GLFW_CONSTANTS.GLFW_CURSOR, GLFW_CONSTANTS.GLFW_CURSOR_HIDDEN)

        self.lastTime = 0
        self.currentTime = 0
        self.numFrames = 0
        self.frameTime = 0

        self.space_down = glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_SPACE) == GLFW_CONSTANTS.GLFW_PRESS

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
                
            if glfw.get_mouse_button(self.window, GLFW_CONSTANTS.GLFW_MOUSE_BUTTON_LEFT) == GLFW_CONSTANTS.GLFW_PRESS:
                self.scene.set_camera_zoom(10)
            if glfw.get_mouse_button(self.window, GLFW_CONSTANTS.GLFW_MOUSE_BUTTON_RIGHT) == GLFW_CONSTANTS.GLFW_PRESS:
                self.scene.set_camera_zoom(5)

            self.handleKeys()
            self.handleMouse()

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
    
    def handleMouse(self):

        
        (x,y) = glfw.get_cursor_pos(self.window)
        rate = self.frameTime / 16.6
        right_amount = -0.1 * rate * ((SCREEN_WIDTH / 2) - x)
        up_amount = -0.1 * rate * ((SCREEN_HEIGHT / 2) - y)
        self.scene.strafe_camera(right_amount, up_amount)
        
        glfw.set_cursor_pos(self.window, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

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