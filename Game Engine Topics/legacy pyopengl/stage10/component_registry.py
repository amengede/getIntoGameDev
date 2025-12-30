from config import *

class ComponentRegistry:

    def __init__(self):

        self.plane_center = np.array([[0, 0, 0]], dtype=np.float32)
        self.plane_theta = np.array([0,], dtype=np.float32)
        self.light_position = np.array([0, 0, 5.0], dtype=np.float32)
        self.ambient_color = np.array([0.5, 0.5, 0.5], dtype=np.float32)
        self.diffuse_color = np.array([0.5, 0.5, 0.5], dtype=np.float32)
        self.camera_position = np.array([0.0, 0.0, 5.0], dtype=np.float32)
        self.camera_eulers = np.array([0.0, 0.0], dtype=np.float32)