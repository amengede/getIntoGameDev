from config import *

class Light:
    """
        Represents a light in the scene
    """


    def __init__(self, position, color, strength, axis, radius, velocity):
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
        self.t = 0
        self.center = np.array(position, dtype=np.float32)
        self.axis = np.array(axis, dtype=np.float32)
        self.radius = radius
        self.velocity = velocity
    
    def update(self, rate):

        self.t += rate
        self.position = self.center + self.radius * self.axis * np.sin(self.velocity * self.t)