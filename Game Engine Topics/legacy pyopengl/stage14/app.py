from config import *
from constants import *
import component_registry
import input_system
import camera_system
import render_system
import world

class App:

    def __init__(self):

        #Set up pygame
        pg.init()
        pg.display.set_mode((640, 480), pg.DOUBLEBUF | pg.OPENGL)
        pg.mouse.set_visible(False)
        self.clock = pg.time.Clock()

        #set up data
        self.component_registry = component_registry.ComponentRegistry()

        #set up systems
        self.world = world.World(self.component_registry)
        self.input_system = input_system.InputSystem(self.component_registry)
        self.camera_system = camera_system.CameraSystem(self.component_registry)
        self.render_system = render_system.RenderSystem(self.component_registry)

        #state
        self.debug_mode = False
        self.camera_system.change_state(STATE_PERSPECTIVE)
        self.world.change_state(STATE_PERSPECTIVE)
        self.render_system.change_state(STATE_PERSPECTIVE)
    
    def run(self):
        running = True
        self.frametime = 0.0
        while running:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        running = False
                    elif event.key == pg.K_t:
                        self.toggle_debug()

            self.input_system.update(self.frametime)
            self.world.update(self.frametime)
            self.camera_system.update(self.frametime)
            drawcalls = self.render_system.update(self.frametime)

            fps = self.clock.get_fps()
            if fps != 0:
                self.frametime = 1000.0 / self.clock.get_fps()
            self.clock.tick()

            pg.display.set_caption(f"Drawcalls: {drawcalls}, Frametime: {round(self.frametime, 2)} ms")

        pg.quit()
    
    def toggle_debug(self) -> None:

        self.debug_mode = not self.debug_mode
        new_state = STATE_TOP_DOWN if self.debug_mode else STATE_PERSPECTIVE
        self.camera_system.change_state(new_state)
        self.world.change_state(new_state)
        self.render_system.change_state(new_state)