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
        self.mouseHover = False
        self.neighbor = False
    
    def setMouseHover(self, mouseHover):
        self.mouseHover = mouseHover
    
    def setNeighbor(self, neighbor):
        self.neighbor = neighbor
    
    def getCartesian(self):
        return (self.x, self.y)
    
    def draw(self, surface):
        color = PALETTE["light-yellow"]
        if self.neighbor and self.mouseHover:
            color = PALETTE["red"]
        if self.neighbor or self.mouseHover:
            pg.draw.rect(surface, color, pg.Rect(self.x,self.y,PIECE_SIZE,PIECE_SIZE))
        surface.blit(CandyPiece.JEWELS[self.type],(self.x+4,self.y+4))