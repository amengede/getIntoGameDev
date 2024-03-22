from config import *

GRID_WIDTH = 20
GRID_HEIGHT = 15
BOX_COUNT_X = SCREEN_WIDTH // GRID_WIDTH
BOX_COUNT_Y = SCREEN_HEIGHT // GRID_HEIGHT

class Particle:


    def __init__(self):
        self.x = random.randrange(0, SCREEN_WIDTH)
        self.y = random.randrange(0, SCREEN_HEIGHT)
        self.vx = 1.0 - 2.0 * random.random()
        self.vy = 1.0 - 2.0 * random.random()

    def get_box_index(self):

        return (int(self.x // GRID_WIDTH), int(self.y // GRID_HEIGHT))
    
class Box:


    def __init__(self, x: float, y: float, w: float, h: float):

        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.particles: list[Particle] = []
    
    def contains(self, x: float, y: float):

        return x >= self.x \
            and x <= (self.x + self.w) \
            and y >= self.y \
            and y <= (self.y + self.h)

    def get_boundary(self, x: float, y:float):

        dx = 0
        dy = 0

        if (x < self.x):
            dx = -1
        elif (x > (self.x + self.w)):
            dx = 1
        
        if (y < self.y):
            dy = -1
        elif (y > (self.y + self.h)):
            dy = 1
        
        return (dx, dy)
    
class World:


    def __init__(self):

        #build particles
        self.particles = [Particle() for _ in range(256)]
        
        #build boxes
        self.boxes: list[list[Box]] = []
        for i in range(BOX_COUNT_Y):
            box_row = []
            for j in range(BOX_COUNT_X):
                box_row.append(Box(j * GRID_WIDTH, i * GRID_HEIGHT, GRID_WIDTH, GRID_HEIGHT))
            self.boxes.append(box_row)
        
        #send particles to boxes
        for particle in self.particles:
            col, row = particle.get_box_index()
            self.boxes[row][col].particles.append(particle)
    
    def update(self, frame_time: float, simulation: bool):

        orphaned_particles: list[Particle] = []

        if simulation:
            self.move_particle(self.particles[0], frame_time)
        
        else:
            for particle in self.particles:
                self.move_particle(particle, frame_time)
        
        for particle in orphaned_particles:
            col, row = particle.get_box_index()
            self.boxes[row][col].particles.append(particle)
    
    def move_particle(self, particle: Particle, frame_time: float):

        col, row = particle.get_box_index()
        self.boxes[row][col].particles.remove(particle)

        new_x = particle.x + frame_time / 16.6 * particle.vx
        #edges
        if new_x <= 0 or new_x >= SCREEN_WIDTH:
            particle.vx *= -1
        else:
            #other particles
            can_move = True
            for box in self.get_x_neighbours(row, col, particle.vx):
                for other in box.particles:
                    if (abs(new_x - other.x) \
                        + abs(particle.y - other.y)) < 4:
                        particle.vx *= -1
                        can_move = False
                        break
                if not can_move:
                    break
            if can_move:
                particle.x = new_x
                col, row = particle.get_box_index()
            
            new_y = particle.y + frame_time / 16.6 * particle.vy
            #edges
            if new_y <= 0 or new_y >= SCREEN_HEIGHT:
                particle.vy *= -1
            else:
                #other particles
                can_move = True
                for box in self.get_y_neighbours(row, col, particle.vy):
                    for other in box.particles:
                        if (abs(particle.x - other.x) \
                            + abs(new_y - other.y)) < 4:
                            particle.vy *= -1
                            can_move = False
                            break
                    if not can_move:
                        break
                if can_move:
                    particle.y = new_y

        col, row = particle.get_box_index()
        self.boxes[row][col].particles.append(particle)
    
    def get_neighbours(self, row: int, col: int):

        neighbours = [self.boxes[row][col]]
        if col > 0:
            if row > 0:
                neighbours.append(self.boxes[row - 1][col - 1])
            neighbours.append(self.boxes[row][col - 1])
            if row < (BOX_COUNT_Y - 1):
                neighbours.append(self.boxes[row + 1][col - 1])
        if row > 0:
            neighbours.append(self.boxes[row - 1][col])
        if row < (BOX_COUNT_Y - 1):
            neighbours.append(self.boxes[row + 1][col])
        if col < BOX_COUNT_X - 1:
            if row > 0:
                neighbours.append(self.boxes[row - 1][col + 1])
            neighbours.append(self.boxes[row][col + 1])
            if row < (BOX_COUNT_Y - 1):
                neighbours.append(self.boxes[row + 1][col + 1])
        return neighbours

    def get_x_neighbours(self, row: int, col: int, vx: float):

        neighbours = [self.boxes[row][col]]
        if vx < 0 and col > 0:
            neighbours.append(self.boxes[row][col - 1])
        elif vx > 0 and col < BOX_COUNT_X - 1:
            neighbours.append(self.boxes[row][col + 1])
        return neighbours
    
    def get_y_neighbours(self, row: int, col: int, vy: float):

        neighbours = [self.boxes[row][col]]
        if vy < 0 and row > 0:
            neighbours.append(self.boxes[row - 1][col])
        elif vy > 0 and row < BOX_COUNT_Y - 1:
            neighbours.append(self.boxes[row + 1][col])
        return neighbours
    
    def get_boxes(self):
        return self.boxes
    
    def get_particles(self):
        return self.particles
