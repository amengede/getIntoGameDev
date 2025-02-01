from config import *

class ComponentRegistry:

    def __init__(self):

        self.camera_position = np.array([0.0, 0.0, 5.0], dtype=np.float32)
        self.camera_eulers = np.array([0.0, 0.0], dtype=np.float32)
        self.camera_velocity = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.walls = None
        self.floors = None
        self.ceilings = None
        self.wall_mask = None
    
    def set_map_size(self, height: int, width: int) -> None:

        self.walls = np.zeros((width, height), dtype=np.int8)
        self.wall_mask = np.zeros((width, height), dtype=np.int8)
        self.ceilings = np.zeros((width, height), dtype=np.int8)
        self.floors = np.zeros((width, height), dtype=np.int8)