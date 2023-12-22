from config import *
import model

class Renderer:


    def __init__(self, surface: pg.Surface):

        self.surface = surface
    
    def draw(self, boxes: list[list[model.Box]], particles: list[model.Particle], simulation: bool):

        self.surface.fill(BLACK)

        particle = particles[0]
        center = (particle.x, particle.y)
        col, row = particle.get_box_index()

        if simulation:
            color = WHITE
            pg.draw.circle(self.surface, color, center, 2)

            for i,box_row in enumerate(boxes):
                for j,box in enumerate(box_row):

                    color = WHITE
                    pg.draw.rect(self.surface, color, pg.Rect(box.x, box.y, box.w, box.h), 1)

                    color = GREEN
                    if i == row and j == col:
                        color = RED

                    for particle in box.particles:
                        center = (particle.x, particle.y)
                        pg.draw.circle(self.surface, color, center, 2)
        else:
            color = GREEN

            for particle in particles:
                center = (particle.x, particle.y)
                pg.draw.circle(self.surface, color, center, 2)

        pg.display.update()