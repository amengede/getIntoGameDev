from config import *
import component_registry
import input_system
import camera_system
import transform_system
import render_system

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
        self.input_system = input_system.InputSystem(self.component_registry)
        self.camera_system = camera_system.CameraSystem(self.component_registry)
        self.transform_system = transform_system.TransformSystem(self.component_registry)
        self.render_system = render_system.RenderSystem(self.component_registry)
    
    def run(self):
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    running = False

            self.input_system.update()
            self.camera_system.update()
            self.transform_system.update()
            self.render_system.update()

            self.clock.tick(60)

        pg.quit()