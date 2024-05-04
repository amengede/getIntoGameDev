from config import *
BG_GRID_SIZE = 128
CROSS_SECTIONAL_AREA = 0.1
DAMPING_COEFFICIENT = 0.08
dl = 8
dx = 0.5

class World:


    def __init__(self):

        #build background
        self.bg = []
        for x in range(0,SCREEN_WIDTH, BG_GRID_SIZE):
            for y in range(0, SCREEN_HEIGHT, BG_GRID_SIZE):
                self.bg.append([x,y])

        #nodes
        self.strands = []
        self.original_strands = []
        for i in range(32):
            strand = []
            original_strand = []
            x = 320 + i * dx
            length = 16 + np.random.randint(16)
            for j in range(length):
                y = 300 + j * dl
                strand.append([x, y, 0.0, 0.0, -90.0])
                original_strand.append([x,y])
            self.strands.append(strand)
            self.original_strands.append(original_strand)
        self.masses = [len(strand) for strand in self.strands]
    
    def update(self, frame_time: float, velocity_x: float, velocity_y: float):

        rate = frame_time / 16.7

        for particle in self.bg:
            particle[0] -= velocity_x * rate
            if particle[0] < 0:
                particle[0] += SCREEN_WIDTH
            if particle[0] > SCREEN_WIDTH:
                particle[0] -= SCREEN_WIDTH
            
            particle[1] -= velocity_y * rate
            if particle[1] < 0:
                particle[1] += SCREEN_HEIGHT
            if particle[1] > SCREEN_HEIGHT:
                particle[1] -= SCREEN_HEIGHT

        for j,strand in enumerate(self.strands):
            
            mass = self.masses[j]
            for i in range(len(strand) - 1, 0, -1):
                point = strand[i]
                parent = strand[i - 1]
                #read data
                dx = point[0] - parent[0]
                dy = point[1] - parent[1]
                axis = np.array((dx,dy,0.0), dtype=np.float32)

                #gravity
                gravity = np.array((0,0.05,0), dtype=np.float32)
                point[3] = np.cross(gravity, axis)[2]

                #wind
                wind = 1 / mass * CROSS_SECTIONAL_AREA * np.array((velocity_x,velocity_y,0), dtype=np.float32)
                point[3] -= np.cross(wind, axis)[2]

                #damping
                point[3] -= DAMPING_COEFFICIENT * point[2]

                point[2] += rate * point[3]
                point[4] += rate * point[2]

                t = np.radians(point[4])
                c = np.cos(t)
                s = np.sin(t)

                point[0] = parent[0] + dl * c
                point[1] = parent[1] - dl * s
    
    def get_bg(self) -> list[tuple[float]]:
        return self.bg
    
    def get_strands(self) -> list[tuple[float]]:
        return self.strands