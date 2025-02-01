from config import *
import component_registry

class TransformSystem:

    def __init__(self, registry: component_registry.ComponentRegistry):

        self.thetas = registry.plane_theta

    def update(self) -> None:

        for i in range(len(self.thetas)):
            self.thetas[i] += 1
            if self.thetas[i] > 360:
                self.thetas[i] -= 360
