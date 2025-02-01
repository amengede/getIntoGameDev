from config import *

class CameraSystem:

    def update(self, position: np.ndarray, eulers: np.ndarray) -> None:

        theta, phi = eulers
        glPushMatrix()
        glRotatef(-phi, 1, 0, 0)
        glRotatef(-theta, 0, 1, 0)
        glTranslatef(*-position)
