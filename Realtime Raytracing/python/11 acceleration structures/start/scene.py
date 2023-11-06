from multiprocessing import parent_process
from config import *
import sphere
import camera
import node

class Scene:
    """
        Holds pointers to all objects in the scene
    """


    def __init__(self):
        """
            Set up scene objects.
        """
        
        sphere_count = 1024
        self.spheres = [
            sphere.Sphere(
                center = [
                    np.random.uniform(low = -95.0, high = 95.0),
                    np.random.uniform(low = -95.0, high = 95.0),
                    np.random.uniform(low = -15.0, high = 15.0)
                ],
                radius = np.random.uniform(low = 0.3, high = 2.0),
                color = [
                    np.random.uniform(low = 0.0, high = 1.0),
                    np.random.uniform(low = 0.0, high = 1.0),
                    np.random.uniform(low = 0.0, high = 1.0)
                ],
                roughness = np.random.uniform(low = 0.0, high = 1.0)
            ) for i in range(sphere_count)
        ]
        
        self.camera = camera.Camera(
            position = [0.0, 0.0, 1.0]
        )

        self.outDated = True
    
    def move_player(self, forwardsSpeed, rightSpeed):
        """
        attempt to move the player with the given speed
        """
        
        dPos = forwardsSpeed * self.camera.forwards + rightSpeed * self.camera.right
        
        self.camera.position[0] += dPos[0]
        self.camera.position[1] += dPos[1]
    
    def spin_player(self, dAngle):
        """
            shift the player's direction by the given amount, in degrees
        """
        self.camera.theta += dAngle[0]
        if (self.camera.theta < 0):
            self.camera.theta += 360
        elif (self.camera.theta > 360):
            self.camera.theta -= 360
        
        self.camera.phi += dAngle[1]
        if (self.camera.phi < -89):
            self.camera.phi = -89
        elif (self.camera.phi > 89):
            self.camera.phi = 89
        
        self.camera.recalculateVectors()