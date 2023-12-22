from config import *
import model

class Renderer:


    def __init__(self, surface: pg.Surface):

        self.surface = surface
    
    def draw(self, particles: list[model.Particle], simulation: bool):

        self.surface.fill(BLACK)

        for i, particle in enumerate(particles):

            color = GREEN
            if simulation:
                color = RED
                if i == 0:
                    color = WHITE
            
            center = (particle.x, particle.y)
            pg.draw.circle(self.surface, color, center, 2)

        pg.display.update()