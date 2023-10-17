from config import *
import sphere
import triangle

class Node:


    def __init__(self):

        self.min_corner = np.array([1e10, 1e10, 1e10], dtype=np.float32)
        self.primitive_count = 0
        self.max_corner = np.array([-1e10, -1e10, -1e10], dtype=np.float32)
        self.contents = -1

    def grow(self, _triangle: triangle.Triangle) -> None:

        for i in range(3):
            
            corner = _triangle.corners[i]
            self.min_corner = np.minimum(self.min_corner, corner)
            self.max_corner = np.maximum(self.max_corner, corner)
    
    def get_cost(self) -> float:

        return self.primitive_count * self.get_surface_area()

    def get_surface_area(self) -> float:

        e = self.max_corner - self.min_corner
        return e[0] * e[1] + e[0] * e[2] + e[1] * e[2]
    
    def __str__(self) -> None:

        result = ""
        node_type = "Internal"
        if self.primitive_count > 0:
            node_type = "External"
        
        result += f"---- {node_type} Node ----\n"

        result += f"\t({self.min_corner[0]}, {self.min_corner[1]}, {self.min_corner[2]})"
        result += f" -> ({self.max_corner[0]}, {self.max_corner[1]}, {self.max_corner[2]})\n"

        if node_type == "Internal":
            self.primitive_count = 2
            result += f"\tCost: {self.get_cost()}\n"
            self.primitive_count = 0
            result += f"\tLeft Child: {self.contents}, Right Child: {self.contents + 1}"
        else:
            result += f"\tPrimitive Count: {self.primitive_count}"
            result += f"\tCost: {self.get_cost()}\n"
            result += f"\tFirst Primitive: {self.contents}, Last Primitive: {self.contents + self.primitive_count - 1}"
        
        return result
