from config import *
from helpers import *
from model import *
from view import *

class App:


    def __init__(self, width: int, height: int):

        self.width = width
        self.height = height
        self.window = make_window(width, height)

        self.renderer = GraphicsEngine(width, height, self.window)

        self.scene = Scene()

        self.last_time = glfw.get_time()
        self.current_time = 0
        self.frames_rendered = 0
        self.frame_time = 0

    def run(self):

        running = True
        while (running):
            #check events
            if glfw.window_should_close(self.window):
                break
            if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_ESCAPE) == GLFW_CONSTANTS.GLFW_PRESS:
                running = False
            glfw.poll_events()
            
            self.handle_keys()
            self.handle_mouse()

            self.scene.update(self.frame_time * 0.05)
            
            self.renderer.render(self.scene)

            #timing
            self.calculate_framerate()
        self.quit()

    def handle_keys(self):

        combo = 0
        direction_modifier = 0
        """
        w: 1 -> 0 degrees
        a: 2 -> 90 degrees
        w & a: 3 -> 45 degrees
        s: 4 -> 180 degrees
        w & s: 5 -> x
        a & s: 6 -> 135 degrees
        w & a & s: 7 -> 90 degrees
        d: 8 -> 270 degrees
        w & d: 9 -> 315 degrees
        a & d: 10 -> x
        w & a & d: 11 -> 0 degrees
        s & d: 12 -> 225 degrees
        w & s & d: 13 -> 270 degrees
        a & s & d: 14 -> 180 degrees
        w & a & s & d: 15 -> x
        """

        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_W) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 1
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_A) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 2
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_S) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 4
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_D) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 8
        
        if combo > 0:
            if combo == 3:
                direction_modifier = 45
            elif combo == 2 or combo == 7:
                direction_modifier = 90
            elif combo == 6:
                direction_modifier = 135
            elif combo == 4 or combo == 14:
                direction_modifier = 180
            elif combo == 12:
                direction_modifier = 225
            elif combo == 8 or combo == 13:
                direction_modifier = 270
            elif combo == 9:
                direction_modifier = 315
            
            dPos = [
                self.frame_time * 0.025 * np.cos(np.deg2rad(self.scene.player.theta + direction_modifier)),
                self.frame_time * 0.025 * np.sin(np.deg2rad(self.scene.player.theta + direction_modifier)),
                0
            ]

            self.scene.move_player(dPos)

    def handle_mouse(self):

        (x,y) = glfw.get_cursor_pos(self.window)
        theta_increment = self.frame_time * 0.05 * ((self.width // 2) - x)
        phi_increment = self.frame_time * 0.05 * ((self.height // 2) - y)
        self.scene.spin_player(theta_increment, phi_increment)
        glfw.set_cursor_pos(self.window, self.width // 2,self.height // 2)

    def calculate_framerate(self):

        self.current_time = glfw.get_time()
        delta = self.current_time - self.last_time
        if (delta >= 1):
            framerate = max(1,int(self.frames_rendered/delta))
            #pg.display.set_caption(f"Running at {framerate} fps.")
            self.renderer.update_fps(framerate)
            self.last_time = self.current_time
            self.frames_rendered = -1
            self.frame_time = float(1000.0 / max(1,framerate))
        self.frames_rendered += 1

    def quit(self):
        
        self.renderer.destroy()