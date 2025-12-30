from config import *

class Sphere:
    """
        Represents a sphere in the scene
    """

    def __init__(self, center, radius, color, roughness, axis, radius_of_motion, velocity):
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
        self.roughness = roughness
        self.t = 0
        self.center_of_motion = np.array(center, dtype=np.float32)
        self.axis = np.array(axis, dtype=np.float32)
        self.radius_of_motion = radius_of_motion
        self.velocity = velocity
    
    def update(self, rate):

        self.t += rate
        self.center = self.center_of_motion + self.radius_of_motion * self.axis * np.sin(self.velocity * self.t)