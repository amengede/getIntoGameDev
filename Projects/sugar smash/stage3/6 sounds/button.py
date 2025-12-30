from config import *

class Button:

    FONT = pg.font.SysFont("lucidaconsole",24)

    def __init__(self,rect,text,onColor, offColor):
        self.rect = rect
        self.text = text
        self.onColor = onColor
        self.offColor = offColor
        self.color = self.offColor
    
    def hasMouse(self):
        (x,y) = pg.mouse.get_pos()
        return (x > self.rect.x and x < self.rect.x + self.rect.w and y > self.rect.y and y < self.rect.y + self.rect.h)
    
    def handleMouse(self):
        if self.hasMouse():
            self.color = self.onColor
        else:
            self.color = self.offColor
    
    def handleMouseClick(self):
        return self.hasMouse()
    
    def draw(self, surface):
        newGameLabel = Button.FONT.render(self.text, True, PALETTE["red"], self.color)
        surface.blit(newGameLabel, self.rect)