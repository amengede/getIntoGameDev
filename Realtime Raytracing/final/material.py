from config import *

class Material:
    """
        A simple, single color material
    """


    def __init__(self, color, reflectance, fuzz):
        """
            Create a new material

            Parameters:
                color (array [3,1])
                reflectance (float) between 0 and 1
                fuzz (float) between 0 and 1
        """

        self.color = np.array(color,dtype=np.float32)
        self.reflectance = reflectance
        self.fuzz = fuzz