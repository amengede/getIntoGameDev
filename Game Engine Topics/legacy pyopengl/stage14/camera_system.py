from config import *
import component_registry
import system
from constants import *

class Perspective(system.State):

    def __init__(self, registry: component_registry.ComponentRegistry):

        self.position = registry.camera_position
        self.eulers = registry.camera_eulers

    def update(self, frametime: float) -> int:
        theta = self.eulers[0]
        glPushMatrix()
        glRotatef(-theta, 0, 1, 0)
        glTranslatef(*-self.position)

        return STATE_NO_CHANGE
    
class TopDown(system.State):

    def __init__(self, registry: component_registry.ComponentRegistry):

        self.position = registry.camera_position
        self.eulers = registry.camera_eulers
        self.height = 10.0

    def update(self, frametime: float) -> int:
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        glTranslatef(-self.position[0], -self.height, -self.position[2])

        return STATE_NO_CHANGE

class CameraSystem(system.System):

    def __init__(self, registry: component_registry.ComponentRegistry):

        super().__init__()

        self.states[STATE_PERSPECTIVE] = Perspective(registry)
        self.states[STATE_TOP_DOWN] = TopDown(registry)
