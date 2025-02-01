from config import *

class CandyPiece:

    JEWELS = {
    "red": pg.image.load("gfx/gem.png").convert_alpha(),
    "orange": pg.image.load("gfx/gem1.png").convert_alpha(),
    "pink": pg.image.load("gfx/gem2.png").convert_alpha(),
    "blue": pg.image.load("gfx/gem3.png").convert_alpha(),
    "green": pg.image.load("gfx/gem4.png").convert_alpha()
    }

    STABLE = 0
    FALLING = 1

    GRAVITY = 0.5
    BOUNCE_AMOUNT = 0.75

    def __init__(self,x,y,type):
        self.type = type
        self.x = x
        self.y = y
        self.groundY = y
        self.velocity = 0
        self.mouseHover = False
        self.neighbor = False
        self.smashed = False
        self.state = CandyPiece.STABLE
    
    def setMouseHover(self, mouseHover):
        self.mouseHover = mouseHover
    
    def setNeighbor(self, neighbor):
        self.neighbor = neighbor
    
    def setSmashed(self, smashed):
        self.smashed = smashed
    
    def setGroundY(self,groundY):
        self.groundY = groundY
    
    def getCartesian(self):
        return (self.x, self.y)
    
    def isStable(self):
        return self.state == CandyPiece.STABLE
    
    def update(self):
        if self.y < self.groundY:
            self.state = CandyPiece.FALLING
        if self.state == CandyPiece.FALLING:
            self.velocity += CandyPiece.GRAVITY
            self.y += self.velocity
            if self.y > self.groundY and abs(self.y - self.groundY) > 2:
                self.velocity *= -CandyPiece.BOUNCE_AMOUNT
            elif self.y > self.groundY:
                self.state = CandyPiece.STABLE
                self.velocity = 0
                self.y = self.groundY
    
    def draw(self, surface, x_offset):
        color = PALETTE["light-yellow"]
        if (self.neighbor and self.mouseHover) or self.smashed:
            color = PALETTE["red"]
        if self.neighbor or self.mouseHover or self.smashed:
            pg.draw.rect(surface, color, pg.Rect(self.x+x_offset,self.y,PIECE_SIZE,PIECE_SIZE))
        surface.blit(CandyPiece.JEWELS[self.type],(self.x+4+x_offset,self.y+4))