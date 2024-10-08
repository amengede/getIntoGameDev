from config import *
import component_registry

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

        self.walls = self.load_array(data, registry.walls)
        
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

        self.floors = self.load_array(data, registry.floors)
        
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

        self.ceilings = self.load_array(data, registry.ceilings)
        
        #player
        self.player_pos = registry.camera_position
        self.player_pos[0] = 15
        self.player_pos[2] = 11
        self.player_eulers = registry.camera_eulers
        self.player_eulers[0] = 180
        self.player_velocity = registry.camera_velocity

    def load_array(self, data: str, src: np.ndarray) -> np.ndarray:

        i = 0
        j = 0
        for element in data.split():
            src[i][j] = int(element)
            j += 1
            if j >= len(src[0]):
                j = 0
                i += 1
        
        return src
    
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