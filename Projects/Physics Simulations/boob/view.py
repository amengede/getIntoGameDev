from config import *
import model

class Renderer:


    def __init__(self, surface: pg.Surface):

        self.surface = surface
    
    def draw(self, bg: list[tuple[float]], 
             control_points: list[tuple[float]], 
             image: list[list[float]]):

        self.surface.fill(BLACK)

        color = GREEN
        for particle in bg:
            pg.draw.circle(self.surface, color, particle, 2)
        
        color = CYAN
        pg.draw.line(self.surface, color, control_points[0], control_points[1])
        pg.draw.circle(self.surface, color, control_points[0], 4)
        pg.draw.circle(self.surface, color, control_points[1], 4)

        color = WHITE
        for i in range(len(image)):
            pg.draw.line(self.surface, color, image[i], image[(i + 1)%len(image)])
        color = RED
        for i in range(len(image)):
            pg.draw.circle(self.surface, color, image[i], 4)

        pg.display.update()