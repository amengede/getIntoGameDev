from config import *
import component_registry

@njit(cache = True)
def record_floor_commands(pos: np.ndarray, eulers: np.ndarray, 
                          floors: np.ndarray, ceilings: np.ndarray,
                          draw_commands: np.ndarray) -> int:

    theta = np.radians(eulers[0])
    c = -np.cos(theta)
    s = -np.sin(theta)
    forwards = np.array((s, 0.0, c), dtype=np.float32)
    threshold = 0.5
    command_count = 0

    row_count, col_count = floors.shape

    for i in range(row_count):
        for j in range(col_count):
            floor_material = floors[i][j]

            if floor_material == 0:
                continue

            floor_pos = np.array((i, 0.0, j), dtype = np.float32)
            to_floor = floor_pos - pos
            magnitude = np.sqrt(np.dot(to_floor, to_floor))
            close = magnitude < 0.001
            to_floor /= magnitude if not close else 1.0
            visible = np.dot(to_floor, forwards) >= threshold
            if not (close or visible):
                continue

            ceiling_material = ceilings[i][j]

            draw_commands[command_count]["i"] = i
            draw_commands[command_count]["j"] = j
            draw_commands[command_count]["floor"] = floor_material
            draw_commands[command_count]["ceiling"] = ceiling_material
            command_count += 1
    return command_count

@njit(cache = True)
def record_wall_commands(pos: np.ndarray, eulers: np.ndarray, 
                          walls: np.ndarray, masks: np.ndarray,
                          draw_commands: np.ndarray) -> int:

    theta = np.radians(eulers[0])
    c = -np.cos(theta)
    s = -np.sin(theta)
    forwards = np.array((s, 0.0, c), dtype=np.float32)
    threshold = 0.0
    command_count = 0

    row_count, col_count = walls.shape

    for i in range(row_count):
        for j in range(col_count):
            material = walls[i][j]

            if material == 0:
                continue

            wall_pos = np.array((i, 0.0, j), dtype = np.float32)
            to_wall = wall_pos - pos

            magnitude = np.sqrt(np.dot(to_wall, to_wall))
            close = magnitude < 0.001
            to_wall /= magnitude if not close else 1.0
            visible = np.dot(to_wall, forwards) >= threshold
            if not close and not visible:
                continue

            mask = masks[i][j]

            draw_commands[command_count]["i"] = i
            draw_commands[command_count]["j"] = j
            draw_commands[command_count]["material"] = material
            draw_commands[command_count]["mask"] = mask
            command_count += 1
    return command_count

class World:

    def __init__(self, registry: component_registry.ComponentRegistry):
        
        registry.set_map_size(27,18)

        #walls
        data = """0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 2 2 2 0 0 
0 0 3 3 3 3 3 3 3 3 0 0 0 0 0 0 0 0 0 0 2 0 0 0 0 2 0 
0 0 3 0 0 0 0 0 0 3 0 0 0 0 0 0 0 0 0 2 0 0 0 0 0 0 2 
0 0 3 0 0 0 0 0 0 3 0 0 0 0 0 0 0 0 2 0 0 0 0 0 0 0 2 
0 0 3 0 0 6 6 0 0 3 2 2 2 2 2 2 2 2 0 0 0 0 0 0 0 0 2 
0 0 3 0 0 6 6 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 
0 0 3 0 0 0 0 0 0 3 2 0 2 2 2 2 2 2 0 0 0 0 0 0 0 0 2 
0 0 3 0 0 0 0 0 3 0 2 0 2 0 0 0 0 0 2 0 0 0 0 0 0 0 2 
0 0 3 0 0 0 0 0 3 0 2 0 2 0 0 0 0 0 0 2 0 0 0 0 0 0 2 
0 0 3 3 3 3 3 3 3 0 1 0 1 0 0 0 0 0 0 0 2 0 0 0 0 2 0 
0 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 2 2 2 2 0 0 
0 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0"""

        wall_count, self.walls = self.load_array(data, registry.walls)
        self.wall_mask = self.mask_out(self.walls, registry.wall_mask)
        registry.record_wall_commands(wall_count)
        
        #floors
        data = """0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 0 0 
0 0 0 5 5 5 5 5 5 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 0 
0 0 0 5 5 5 5 5 5 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 0 
0 0 0 5 5 0 0 5 5 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 0 
0 0 0 5 5 0 0 5 5 3 3 3 3 3 3 3 3 3 1 1 1 1 1 1 1 1 0 
0 0 0 5 5 5 5 5 5 0 0 3 0 0 0 0 0 0 1 1 1 1 1 1 1 1 0 
0 0 0 5 5 5 5 5 0 0 0 3 0 0 0 0 0 0 0 1 1 1 1 1 1 1 0 
0 0 0 5 5 5 5 5 0 0 0 3 0 0 0 0 0 0 0 0 1 1 1 1 1 1 0 
0 0 0 0 0 0 0 0 0 0 0 3 0 0 0 0 0 0 0 0 0 1 1 1 1 0 0 
0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"""

        _, self.floors = self.load_array(data, registry.floors)
        
        #ceilings
        data = """0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 2 2 2 0 0 
0 0 0 6 6 6 6 6 6 0 0 0 0 0 0 0 0 0 0 0 2 2 2 2 2 2 0 
0 0 0 6 6 6 6 6 6 0 0 0 0 0 0 0 0 0 0 2 2 2 2 2 2 2 0 
0 0 0 6 6 0 0 6 6 0 0 0 0 0 0 0 0 0 2 2 2 2 2 2 2 2 0 
0 0 0 6 6 0 0 6 6 4 4 4 4 4 4 4 4 4 2 2 2 2 2 2 2 2 0 
0 0 0 6 6 6 6 6 6 0 0 4 0 0 0 0 0 0 2 2 2 2 2 2 2 2 0 
0 0 0 6 6 6 6 6 0 0 0 4 0 0 0 0 0 0 0 2 2 2 2 2 2 2 0 
0 0 0 6 6 6 6 6 0 0 0 4 0 0 0 0 0 0 0 0 2 2 2 2 2 2 0 
0 0 0 0 0 0 0 0 0 0 0 4 0 0 0 0 0 0 0 0 0 2 2 2 2 0 0 
0 0 0 0 0 0 0 0 0 0 2 2 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 2 2 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 2 2 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 2 2 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 2 2 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"""

        ceiling_count, self.ceilings = self.load_array(data, registry.ceilings)
        registry.record_floor_commands(ceiling_count)
        
        #player
        self.player_pos = registry.camera_position
        self.player_pos[0] = 15
        self.player_pos[2] = 11
        self.player_eulers = registry.camera_eulers
        self.player_eulers[0] = 180
        self.player_velocity = registry.camera_velocity

        self.registry = registry

    def load_array(self, data: str, src: np.ndarray) -> tuple[int, np.ndarray]:

        element_count = 0

        i = 0
        j = 0
        for element in data.split():
            if element != "0":
                element_count += 1
            src[i][j] = int(element)
            j += 1
            if j >= len(src[0]):
                j = 0
                i += 1
        
        return element_count, src
    
    def mask_out(self, data: np.ndarray, mask: np.ndarray) -> np.ndarray:

        i = 0
        j = 0
        row_count, col_count = data.shape
        for i in range(row_count):
            for j in range(col_count):
                if (data[i][j]) != 0:
                    mask[i][j] = 15
        
        #east walls
        for i in range(row_count):
            mask[i][col_count - 1] &= ~2
        for i in range(row_count):
            for j in range(col_count - 1):
                if (data[i][j + 1]) != 0:
                    mask[i][j] &= ~2
        
        #west walls
        for i in range(row_count):
            mask[i][0] &= ~1
        for i in range(row_count):
            for j in range(1, col_count):
                if (data[i][j - 1]) != 0:
                    mask[i][j] &= ~1
        
        #north walls
        for j in range(col_count):
            mask[row_count - 1][j] &= ~8
        for i in range(row_count - 1):
            for j in range(col_count):
                if (data[i + 1][j]) != 0:
                    mask[i][j] &= ~8
        
        #south walls
        for j in range(col_count):
            mask[0][j] &= ~4
        for i in range(1, row_count):
            for j in range(col_count):
                if (data[i - 1][j]) != 0:
                    mask[i][j] &= ~4
        
        return mask
    
    def update(self) -> None:

        #x movement
        x = round(self.player_pos[0] + 4 * self.player_velocity[0])
        z = round(self.player_pos[2])
        can_move = self.walls[x][z] == 0

        if can_move:
            self.player_pos[0] += self.player_velocity[0]
        
        #x movement
        x = round(self.player_pos[0])
        z = round(self.player_pos[2] + 4 * self.player_velocity[2])
        can_move = self.walls[x][z] == 0

        if can_move:
            self.player_pos[2] += self.player_velocity[2]

        self.registry.floor_command_count = record_floor_commands(
            self.player_pos, self.player_eulers, 
            self.floors, self.ceilings, self.registry.floor_commands)
        
        self.registry.wall_command_count = record_wall_commands(
            self.player_pos, self.player_eulers, 
            self.walls, self.wall_mask, self.registry.wall_commands)