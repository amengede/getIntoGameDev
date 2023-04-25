from config import *

class Sphere:
    """
        Represents a sphere in the scene
    """

    def __init__(self, center: np.ndarray, radius: float, color: np.ndarray):
        """
            Create a new sphere

            Parameters:
                center (array [3,1])
                radius (float)
                color (array [3,1])
        """

        self.center = np.array(center,dtype=np.float32)
        self.radius = radius
        self.color = np.array(color, dtype=np.float32)