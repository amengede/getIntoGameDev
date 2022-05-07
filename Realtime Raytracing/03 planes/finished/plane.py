from config import *

class Plane:
    """
        Represents a plane in the scene
    """


    def __init__(self, normal, tangent, bitangent, uMin, uMax, vMin, vMax, center, color):
        """
            Create a new plane

            Parameters:
                normal (array [3,1])
                tangent (array [3,1])
                bitangent (array [3,1])
                uMin,uMax,vMin,vMax (float) constraints, u: tangent, v: bitangent
                center (array [3,1])
                color (array [3,1])
        """

        self.normal = np.array(normal, dtype=np.float32)
        self.tangent = np.array(tangent, dtype=np.float32)
        self.bitangent = np.array(bitangent, dtype=np.float32)
        self.uMin = uMin
        self.uMax = uMax
        self.vMin = vMin
        self.vMax = vMax
        self.center = np.array(center, dtype=np.float32)
        self.color = np.array(color, dtype=np.float32)