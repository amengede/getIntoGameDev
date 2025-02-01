from config import *

class Particle:


    def __init__(self):
        self.x = random.randrange(0, SCREEN_WIDTH)
        self.y = random.randrange(0, SCREEN_HEIGHT)
        self.vx = 1.0 - 2.0 * random.random()
        self.vy = 1.0 - 2.0 * random.random()

class World:


    def __init__(self):

        self.particles = [Particle() for _ in range(256)]
    
    def update(self, frame_time: float, simulation: bool):

        if simulation:
            self.move_particle(0, frame_time)
        
        else:
            for i in range(len(self.particles)):
                self.move_particle(i, frame_time)
    
    def get_particles(self):
        return self.particles
    
    def move_particle(self, i: int, frame_time: float):

        particle = self.particles[i]
        new_x = particle.x + frame_time / 16.6 * particle.vx
        #edges
        if new_x <= 0 or new_x >= SCREEN_WIDTH:
            particle.vx *= -1
        else:
            #other particles
            can_move = True
            for j, other in enumerate(self.particles):
                if i == j:
                    continue
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
            for j, other in enumerate(self.particles):
                if i == j:
                    continue
                if (abs(particle.x - other.x) \
                    + abs(new_y - other.y)) < 2:
                    particle.vy *= -1
                    can_move = False
                    break
            if can_move:
                particle.y = new_y