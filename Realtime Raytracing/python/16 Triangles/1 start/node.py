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
    
    def __str__(self) -> None:

        result = ""
        node_type = "Internal"
        if self.sphere_count > 0:
            node_type = "External"
        
        result += f"---- {node_type} Node ----\n"

        result += f"\t({self.min_corner[0]}, {self.min_corner[1]}, {self.min_corner[2]})"
        result += f" -> ({self.max_corner[0]}, {self.max_corner[1]}, {self.max_corner[2]})\n"

        if node_type == "Internal":
            self.sphere_count = 2
            result += f"\tCost: {self.get_cost()}\n"
            self.sphere_count = 0
            result += f"\tLeft Child: {self.contents}, Right Child: {self.contents + 1}"
        else:
            result += f"\tSphere Count: {self.sphere_count}"
            result += f"\tCost: {self.get_cost()}\n"
            result += f"\tFirst Sphere: {self.contents}, Last Sphere: {self.contents + self.sphere_count - 1}"
        
        return result
