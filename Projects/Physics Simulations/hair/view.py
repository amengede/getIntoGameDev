from config import *

class Renderer:


    def __init__(self, surface: pg.Surface):

        self.surface = surface
    
    def draw(self, bg: list[tuple[float]], 
             strands: list[tuple[float]]):

        self.surface.fill(BLACK)

        color = GREEN
        for particle in bg:
            pg.draw.circle(self.surface, color, particle, 2)

        color = WHITE
        for strand in strands:
            for i in range(len(strand) - 1):
                x,y,vel,f, theta = strand[i]
                x2,y2,vel,f,theta = strand[i + 1]
                #print(x2, y2)
                pg.draw.line(self.surface, color, (int(x),int(y)), (int(x2),int(y2)))

        pg.display.update()