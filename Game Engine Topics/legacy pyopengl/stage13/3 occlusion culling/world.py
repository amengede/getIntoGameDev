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

@njit(cache = True)
def record_draw_commands(player_state: tuple[np.ndarray,np.ndarray], 
                         world_state: tuple[np.ndarray],
                         output: tuple[np.ndarray], 
                         debug_info: tuple[np.ndarray]) -> tuple[int]:

    #unpack data
    pos, eulers = player_state
    floors, ceilings, walls, wall_mask, visited_mask = world_state
    wall_commands, floor_commands = output
    ray_xs, ray_zs, ray_events = debug_info

    #variables to return
    wall_count = 0
    floor_count = 0

    #setup
    ray_x = pos[0]
    ray_z = pos[2]
    detail = 256
    dx = -np.sin(np.radians(eulers[0]))
    dz = -np.cos(np.radians(eulers[0]))

    #record initial tile
    map_x = round(ray_x)
    map_z = round(ray_z)
    visited_mask[map_x][map_z] = 1

    #tile has floor
    if (floors[map_x][map_z] != 0):
        floor_commands[floor_count]["i"] = map_x
        floor_commands[floor_count]["j"] = map_z
        floor_commands[floor_count]["floor"] = floors[map_x][map_z]
        floor_commands[floor_count]["ceiling"] = ceilings[map_x][map_z]
        floor_count += 1
        
    #tile has wall
    if (walls[map_x][map_z] != 0):
        wall_commands[wall_count]["i"] = map_x
        wall_commands[wall_count]["j"] = map_z
        wall_commands[wall_count]["material"] = walls[map_x][map_z]
        wall_commands[wall_count]["mask"] = wall_mask[map_x][map_z]
        wall_count += 1

    for i in range(detail):

        horizontal_coefficient = i / (detail / 2) - 1
        ray_dx = dx - horizontal_coefficient * dz
        ray_dz = dz + horizontal_coefficient * dx
        depth = 0

        delta_x = 1e30 if ray_dx == 0 else 1 / abs(ray_dx)
        delta_z = 1e30 if ray_dz == 0 else 1 / abs(ray_dz)

        map_x = int(ray_x)
        map_z = int(ray_z)

        side_dist_x = 0.0
        side_dist_z = 0.0
        step_x = 0
        step_z = 0
        
        if (ray_dx < 0):
            step_x = -1
            side_dist_x = (ray_x - map_x) * delta_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1 - ray_x) * delta_x
        if (ray_dz < 0):
            step_z = -1
            side_dist_z = (ray_z - map_z) * delta_z
        else:
            step_z = 1
            side_dist_z = (map_z + 1 - ray_z) * delta_z

        #trace!
        while True:

            if side_dist_x < side_dist_z:
                side_dist_x += delta_x
                map_x += step_x
                depth = side_dist_x
            
            else:
                side_dist_z += delta_z
                map_z += step_z
                depth = side_dist_z

            #tile already visited
            if (visited_mask[map_x][map_z] == 1):
                #...and hit a wall
                if (wall_mask[map_x][map_z] != 0):
                    break
                continue

            visited_mask[map_x][map_z] = 1

            #tile has floor
            if (floors[map_x][map_z] != 0):
                floor_commands[floor_count]["i"] = map_x
                floor_commands[floor_count]["j"] = map_z
                floor_commands[floor_count]["floor"] = floors[map_x][map_z]
                floor_commands[floor_count]["ceiling"] = ceilings[map_x][map_z]
                floor_count += 1
                continue
            
            #tile has wall
            if (walls[map_x][map_z] != 0):
                wall_commands[wall_count]["i"] = map_x
                wall_commands[wall_count]["j"] = map_z
                wall_commands[wall_count]["material"] = walls[map_x][map_z]
                wall_commands[wall_count]["mask"] = wall_mask[map_x][map_z]
                wall_count += 1
                break

            #some invalid state
            break
        ray_xs[i] = ray_x + depth * ray_dx
        ray_zs[i] = ray_z + depth * ray_dz
            
    return wall_count, floor_count

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

        #pack data
        self.player_state = (self.player_pos, self.player_eulers)
        self.world_state = (
            self.floors, self.ceilings, self.walls, self.wall_mask, registry.visited_mask)
        self.command_lists = (registry.wall_commands, registry.floor_commands)
        self.debug_info = (registry.ray_x, registry.ray_z, registry.ray_event)

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
        
        #z movement
        x = round(self.player_pos[0])
        z = round(self.player_pos[2] + 4 * self.player_velocity[2])
        can_move = self.walls[x][z] == 0

        if can_move:
            self.player_pos[2] += self.player_velocity[2]

        """
        self.registry.floor_command_count = record_floor_commands(
            self.player_pos, self.player_eulers, 
            self.floors, self.ceilings, self.registry.floor_commands)
        
        self.registry.wall_command_count = record_wall_commands(
            self.player_pos, self.player_eulers, 
            self.walls, self.wall_mask, self.registry.wall_commands)
        """
        self.registry.visited_mask[:][:] &= 0
        wall_count, floor_count = record_draw_commands(
            self.player_state, self.world_state, 
            self.command_lists, self.debug_info)
        self.registry.wall_command_count = wall_count
        self.registry.floor_command_count = floor_count