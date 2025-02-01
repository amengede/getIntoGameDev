from config import *

class CandyPiece:

    JEWELS = {
    "red": pg.image.load("gfx/gem.png").convert_alpha(),
    "orange": pg.image.load("gfx/gem1.png").convert_alpha(),
    "pink": pg.image.load("gfx/gem2.png").convert_alpha(),
    "blue": pg.image.load("gfx/gem3.png").convert_alpha(),
    "green": pg.image.load("gfx/gem4.png").convert_alpha()
    }

    def __init__(self,x,y,type):
        self.type = type
        self.x = x
        self.y = y
    
    def draw(self, surface):
        surface.blit(CandyPiece.JEWELS[self.type],(self.x+4,self.y+4))