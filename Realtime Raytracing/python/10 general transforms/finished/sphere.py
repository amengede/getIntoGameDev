from config import *

class Sphere:
    """
        Represents a sphere in the scene
    """

    def __init__(self, center, radii, eulers, color, roughness):
        """
            Create a new sphere

            Parameters:
                center (array [3,1])
                radii (array [3,1])
                eulers (array [3,1])
                color (array [3,1])
        """

        self.center = np.array(center,dtype=np.float32)
        self.radii = np.array(radii,dtype=np.float32)
        self.eulers = np.array(eulers,dtype=np.float32)
        self.color = np.array(color, dtype=np.float32)
        self.roughness = roughness