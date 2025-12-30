from config import *
import model

class Renderer:


    def __init__(self, surface: pg.Surface):

        self.surface = surface
    
    def draw(self, boxes: list[list[model.Box]], simulation: bool):

        self.surface.fill(BLACK)

        for i,box_row in enumerate(boxes):
            for j,box in enumerate(box_row):

                color = WHITE
                if simulation and i == 0 and j == 0:
                    color = RED
                
                pg.draw.rect(self.surface, color, pg.Rect(box.x, box.y, box.w, box.h), 1)

                color = GREEN
                if simulation and i == 0 and j == 0:
                    color = RED

                for particle in box.particles:
                    center = (particle.x, particle.y)
                    pg.draw.circle(self.surface, color, center, 2)

        pg.display.update()