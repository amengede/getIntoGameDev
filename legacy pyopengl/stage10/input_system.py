from config import *
import component_registry

class InputSystem:

    def __init__(self, registry: component_registry.ComponentRegistry):

        self.position = registry.camera_position
        self.eulers = registry.camera_eulers

    def update(self) -> None:

        self.handle_keys()
        self.handle_mouse()

    def handle_keys(self) -> None:

        theta_forwards = math.radians(self.eulers[0])
        cos_theta_forwards = math.cos(theta_forwards)
        sin_theta_forwards = math.sin(theta_forwards)

        theta_right = math.radians(self.eulers[0] + 90)
        cos_theta_right = math.cos(theta_right)
        sin_theta_right = math.sin(theta_right)

        keys = pg.key.get_pressed()
        speed = 0.1
        if keys[pg.K_a]:
            self.position[0] -= speed * sin_theta_right
            self.position[2] -= speed * cos_theta_right
        if keys[pg.K_d]:
            self.position[0] += speed * sin_theta_right
            self.position[2] += speed * cos_theta_right
        if keys[pg.K_w]:
            self.position[0] -= speed * sin_theta_forwards
            self.position[2] -= speed * cos_theta_forwards
        if keys[pg.K_s]:
            self.position[0] += speed * sin_theta_forwards
            self.position[2] += speed * cos_theta_forwards

    def handle_mouse(self) -> None:
        current_pos = pg.mouse.get_pos()
        speed = 0.1

        dx = current_pos[0] - 320
        dy = 240 - current_pos[1]
        if abs(dx) + abs(dy) > 0:

            #theta
            self.eulers[0] -= speed * dx
            if self.eulers[0] > 360:
                self.eulers[0] -= 360
            if self.eulers[0] < 0:
                self.eulers[0] += 360
            
            #phi
            self.eulers[1] = min(89, max(-89, self.eulers[1] + speed * dy))

            pg.mouse.set_pos(320, 240)
