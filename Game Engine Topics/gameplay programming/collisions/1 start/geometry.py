from config import *

class Box3D:

    
    def __init__(self, l, w, h, center):

        self.center = np.array(center, dtype=np.float32)
        self.l = l
        self.w = w
        self.h = h