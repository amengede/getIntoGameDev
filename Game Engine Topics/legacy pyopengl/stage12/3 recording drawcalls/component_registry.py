from config import *
from constants import *

class ComponentRegistry:

    def __init__(self):

        self.camera_position = np.array([0.0, 0.0, 5.0], dtype=np.float32)
        self.camera_eulers = np.array([0.0, 0.0], dtype=np.float32)
        self.camera_velocity = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.walls = None
        self.floors = None
        self.ceilings = None
        self.wall_mask = None
        self.floor_commands = None
        self.wall_commands = None
    
    def set_map_size(self, height: int, width: int) -> None:

        self.walls = np.zeros((width, height), dtype=np.int8)
        self.wall_mask = np.zeros((width, height), dtype=np.int8)
        self.ceilings = np.zeros((width, height), dtype=np.int8)
        self.floors = np.zeros((width, height), dtype=np.int8)

    def record_floor_commands(self, command_count: int) -> None:

        self.floor_commands = np.zeros(command_count, dtype = FLOOR_DRAWCALL)

        row_count, col_count = self.floors.shape
        offset = 0

        for i in range(row_count):
            for j in range(col_count):
                floor_material = self.floors[i][j]

                if floor_material == 0:
                    continue

                ceiling_material = self.ceilings[i][j]
                self.floor_commands[offset]["i"] = i
                self.floor_commands[offset]["j"] = j
                self.floor_commands[offset]["floor"] = floor_material
                self.floor_commands[offset]["ceiling"] = ceiling_material

                offset += 1

    def record_wall_commands(self, command_count: int) -> None:

        self.wall_commands = np.zeros(command_count, dtype = WALL_DRAWCALL)

        row_count, col_count = self.walls.shape
        offset = 0

        for i in range(row_count):
            for j in range(col_count):
                wall_material = self.walls[i][j]

                if wall_material == 0:
                    continue

                mask = self.wall_mask[i][j]
                self.wall_commands[offset]["i"] = i
                self.wall_commands[offset]["j"] = j
                self.wall_commands[offset]["material"] = wall_material
                self.wall_commands[offset]["mask"] = mask

                offset += 1