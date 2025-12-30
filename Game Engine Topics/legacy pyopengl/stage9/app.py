from config import *
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
        self.plane_center = np.array([[0, 0, 0]], dtype=np.float32)
        self.plane_theta = np.array([0,], dtype=np.float32)
        self.light_position = np.array([0, 0, 5.0], dtype=np.float32)
        self.ambient_color = np.array([0.5, 0.5, 0.5], dtype=np.float32)
        self.diffuse_color = np.array([0.5, 0.5, 0.5], dtype=np.float32)
        self.camera_position = np.array([0.0, 0.0, 5.0], dtype=np.float32)
        self.camera_eulers = np.array([0.0, 0.0], dtype=np.float32)

        #set up systems
        self.input_system = input_system.InputSystem()
        self.camera_system = camera_system.CameraSystem()
        self.transform_system = transform_system.TransformSystem()
        self.render_system = render_system.RenderSystem()
    
    def run(self):
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    running = False

            self.input_system.update(self.camera_position, self.camera_eulers)
            self.camera_system.update(self.camera_position, self.camera_eulers)
            self.transform_system.update(self.plane_theta)
            self.render_system.update(self.plane_center, self.plane_theta, 
                                      self.light_position, self.ambient_color, 
                                      self.diffuse_color)

            self.clock.tick(60)

        pg.quit()