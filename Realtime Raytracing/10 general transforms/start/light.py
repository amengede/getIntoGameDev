from config import *

class Light:
    """
        Represents a light in the scene
    """


    def __init__(self, position, color, strength):
        """
            Create a new plane

            Parameters:
                position (array [3,1])
                color (array [3,1])
                strength float
        """

        self.position = np.array(position, dtype=np.float32)
        self.color = np.array(color, dtype=np.float32)
        self.strength = strength