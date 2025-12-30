from config import *

class Node:


    def __init__(self):

        self.min_corner = None
        self.max_corner = None
        self.left_child = -1.0
        self.right_child = -1.0
        self.parent = -1.0
        self.first_sphere_index = 0
        self.sphere_count = 0
        self.index = 0
        self.hit_link = -1.0
        self.miss_link = -1.0

class AABB:


    def __init__(self):

        self.min_corner = np.array([1e30, 1e30, 1e30], dtype=np.float32)
        self.max_corner = np.array([-1e30, -1e30, -1e30], dtype=np.float32)

    def grow(self, new_point):

        self.min_corner[0] = min(self.min_corner[0], new_point[0])
        self.min_corner[1] = min(self.min_corner[1], new_point[1])
        self.min_corner[2] = min(self.min_corner[2], new_point[2])

        self.max_corner[0] = max(self.max_corner[0], new_point[0])
        self.max_corner[1] = max(self.max_corner[1], new_point[1])
        self.max_corner[2] = max(self.max_corner[2], new_point[2])
    
    def area(self):

        extent = self.max_corner - self.min_corner
        return float(extent[0]) * float(extent[1]) + float(extent[0]) * float(extent[2]) + float(extent[1]) * float(extent[2])
