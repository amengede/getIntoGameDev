from config import *

class Box:

    def __init__(self, min_corner, max_corner):

        self.min_corner = np.array(min_corner, dtype=np.float32)
        self.max_corner = np.array(max_corner, dtype=np.float32)
    
    def overlaps_with(self, _sphere):

        if (_sphere.center[0] - _sphere.radius) > self.max_corner[0]:
            return False
        elif (_sphere.center[0] + _sphere.radius) < self.min_corner[0]:
            return False
        elif (_sphere.center[1] - _sphere.radius) > self.max_corner[1]:
            return False
        elif (_sphere.center[1] + _sphere.radius) < self.min_corner[1]:
            return False
        elif (_sphere.center[2] - _sphere.radius) > self.max_corner[2]:
            return False
        elif (_sphere.center[2] + _sphere.radius) < self.min_corner[2]:
            return False
        return True