from config import *

GRID_WIDTH = 80
GRID_HEIGHT = 60

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
    
    def move_particles(self, 
        frame_time: float, orphaned_particles: list[Particle]):

        for particle in self.particles:
            new_x = particle.x + frame_time / 16.6 * particle.vx
            #edges
            if new_x <= 0 or new_x >= SCREEN_WIDTH:
                particle.vx *= -1
            else:
                #other particles
                can_move = True
                for other in self.particles:
                    if particle is other:
                        continue
                    if (abs(new_x - other.x) \
                        + abs(particle.y - other.y)) < 2:
                        particle.vx *= -1
                        can_move = False
                        break
                if can_move:
                    for other in orphaned_particles:
                        if (abs(new_x - other.x) \
                            + abs(particle.y - other.y)) < 2:
                            particle.vx *= -1
                            can_move = False
                            break
                if can_move:
                    particle.x = new_x
        
                new_y = particle.y + frame_time / 16.6 * particle.vy
                #edges
                if new_y <= 0 or new_y >= SCREEN_HEIGHT:
                    particle.vy *= -1
                else:
                    #other particles
                    can_move = True
                    for other in self.particles:
                        if particle is other:
                            continue
                        if (abs(particle.x - other.x) \
                            + abs(new_y - other.y)) < 2:
                            particle.vy *= -1
                            can_move = False
                            break
                    if can_move:
                        for other in orphaned_particles:
                            if (abs(particle.x - other.x) \
                                + abs(new_y - other.y)) < 2:
                                particle.vy *= -1
                                can_move = False
                                break
                    if can_move:
                        particle.y = new_y

            if not (self.contains(particle.x, particle.y)):
                orphaned_particles.append(particle)
                self.particles.remove(particle)

class World:


    def __init__(self):

        #build particles
        self.particles = [Particle() for _ in range(256)]
        
        #build boxes
        box_count_x = SCREEN_WIDTH // GRID_WIDTH
        box_count_y = SCREEN_HEIGHT // GRID_HEIGHT
        self.boxes: list[list[Box]] = []
        for i in range(box_count_y):
            box_row = []
            for j in range(box_count_x):
                box_row.append(Box(j * GRID_WIDTH, i * GRID_HEIGHT, GRID_WIDTH, GRID_HEIGHT))
            self.boxes.append(box_row)
        
        #send particles to boxes
        for particle in self.particles:
            col, row = particle.get_box_index()
            self.boxes[row][col].particles.append(particle)
    
    def update(self, frame_time: float, simulation: bool):

        orphaned_particles: list[Particle] = []

        if simulation:
            self.boxes[0][0].move_particles(frame_time, orphaned_particles)
        
        else:
            self.full_update(frame_time, orphaned_particles)
        
        for particle in orphaned_particles:
            col, row = particle.get_box_index()
            self.boxes[row][col].particles.append(particle)
    
    def full_update(self, 
        frame_time: float, orphaned_particles: list[Particle]):

        for box_row in self.boxes:
            for box in box_row:
                box.move_particles(frame_time, orphaned_particles)
    
    def get_boxes(self):
        return self.boxes
    
    def get_particles(self):
        return self.particles
