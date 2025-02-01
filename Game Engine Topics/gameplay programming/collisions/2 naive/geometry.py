from config import *

class Box3D:

    
    def __init__(self, l, w, h, center):

        self.center = np.array(center, dtype=np.float32)
        self.l = l
        self.w = w
        self.h = h
    
    def overlaps_with(self, other):

        if (self.center[0] + self.l / 2) < (other.center[0] - other.l / 2):
            return False

        if (self.center[0] - self.l / 2) > (other.center[0] + other.l / 2):
            return False
        
        if (self.center[1] + self.w / 2) < (other.center[1] - other.w / 2):
            return False

        if (self.center[1] - self.w / 2) > (other.center[1] + other.w / 2):
            return False
        
        if (self.center[2] + self.h / 2) < (other.center[2] - other.h / 2):
            return False

        if (self.center[2] - self.h / 2) > (other.center[2] + other.h / 2):
            return False
        
        return True