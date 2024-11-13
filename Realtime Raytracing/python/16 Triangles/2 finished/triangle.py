from config import *

class Triangle:


    def __init__(self, corners: list[list[float]], color: list[float]):

        self.corners = [
            np.array(corner, dtype=np.float32) for corner in corners]
        
        self.centroid = 0.333 * (
            self.corners[0] + self.corners[1] + self.corners[2])
        
        ab = self.corners[1] - self.corners[0]
        ac = self.corners[2] - self.corners[0]
        self.normal = pyrr.vector.normalize(pyrr.vector3.cross(ab, ac))

        self.color = color