from config import *
import component_registry

class CameraSystem:

    def __init__(self, registry: component_registry.ComponentRegistry):

        self.position = registry.camera_position
        self.eulers = registry.camera_eulers

    def update(self) -> None:

        theta, phi = self.eulers
        glPushMatrix()
        #glRotatef(-phi, 1, 0, 0)
        glRotatef(-theta, 0, 1, 0)
        glTranslatef(*-self.position)
