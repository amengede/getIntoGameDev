from config import *

class InputSystem:

    def update(self, position: np.ndarray, eulers: np.ndarray) -> None:

        self.handle_keys(position, eulers)
        self.handle_mouse(eulers)

    def handle_keys(self, position: list[float], eulers: list[float]) -> None:

        theta_forwards = math.radians(eulers[0])
        cos_theta_forwards = math.cos(theta_forwards)
        sin_theta_forwards = math.sin(theta_forwards)

        theta_right = math.radians(eulers[0] + 90)
        cos_theta_right = math.cos(theta_right)
        sin_theta_right = math.sin(theta_right)

        keys = pg.key.get_pressed()
        speed = 0.1
        if keys[pg.K_a]:
            position[0] -= speed * sin_theta_right
            position[2] -= speed * cos_theta_right
        if keys[pg.K_d]:
            position[0] += speed * sin_theta_right
            position[2] += speed * cos_theta_right
        if keys[pg.K_w]:
            position[0] -= speed * sin_theta_forwards
            position[2] -= speed * cos_theta_forwards
        if keys[pg.K_s]:
            position[0] += speed * sin_theta_forwards
            position[2] += speed * cos_theta_forwards

    def handle_mouse(self, eulers: list[float]) -> None:
        current_pos = pg.mouse.get_pos()
        speed = 0.1

        dx = current_pos[0] - 320
        dy = 240 - current_pos[1]
        if abs(dx) + abs(dy) > 0:

            #theta
            eulers[0] -= speed * dx
            if eulers[0] > 360:
                eulers[0] -= 360
            if eulers[0] < 0:
                eulers[0] += 360
            
            #phi
            eulers[1] = min(89, max(-89, eulers[1] + speed * dy))

            pg.mouse.set_pos(320, 240)
