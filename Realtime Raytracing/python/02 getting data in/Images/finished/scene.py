from config import *
import sphere
import camera

class Scene:
    """
        Holds pointers to all objects in the scene
    """


    def __init__(self):
        """
            Set up scene objects.
        """
        
        self.spheres = [
            sphere.Sphere(
                center = [
                    np.random.uniform(low = 3.0, high = 10.0),
                    np.random.uniform(low = -8.0, high = 8.0),
                    np.random.uniform(low = -8.0, high = 8.0)
                ],
                radius = np.random.uniform(low = 0.1, high = 2.0),
                color = [
                    np.random.uniform(low = 0.3, high = 1.0),
                    np.random.uniform(low = 0.3, high = 1.0),
                    np.random.uniform(low = 0.3, high = 1.0)
                ]
            ) for i in range(32)
        ]
        self.camera = camera.Camera(
            position = [0, 0, 0]
        )