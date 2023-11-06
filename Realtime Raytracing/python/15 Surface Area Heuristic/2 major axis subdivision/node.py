from config import *
import sphere

class Node:


    def __init__(self):

        self.min_corner = np.array([1e10, 1e10, 1e10], dtype=np.float32)
        self.sphere_count = 0
        self.max_corner = np.array([-1e10, -1e10, -1e10], dtype=np.float32)
        self.contents = -1

    def grow(self, _sphere: sphere.Sphere) -> None:

        sphere_min = _sphere.center - _sphere.radius * np.array([1, 1, 1], dtype=np.float32)
        self.min_corner = np.minimum(self.min_corner, sphere_min)

        sphere_max = _sphere.center + _sphere.radius * np.array([1, 1, 1], dtype=np.float32)
        self.max_corner = np.maximum(self.max_corner, sphere_max)
    
    def get_cost(self) -> float:

        return self.sphere_count * self.get_surface_area()

    def get_surface_area(self) -> float:

        e = self.max_corner - self.min_corner
        return e[0] * e[1] + e[0] * e[2] + e[1] * e[2]
