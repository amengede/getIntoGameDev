from config import *

class Sphere:
    """
        Represents a sphere in the scene
    """

    def __init__(self, center, radius, material):
        """
            Create a new sphere

            Parameters:
                center (array [3,1])
                radius (float)
                material (int): material index
        """

        self.center = np.array(center,dtype=np.float32)
        self.radius = radius
        self.material = material