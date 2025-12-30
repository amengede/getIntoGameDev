import pygame as pg
import random
pg.init()

# global variables
SCREEN_SIZE = (300,600)
screen = pg.display.set_mode(SCREEN_SIZE)
PALETTE = {
    "teal":(41,127,135),
    "yellow":(246,209,103),
    "light-yellow":(255,247,174),
    "red":(223,46,46)
}
TYPES = ["red", "orange", "pink", "blue", "green"]
JEWELS = {
    "red": pg.image.load("gfx/gem.png").convert_alpha(),
    "orange": pg.image.load("gfx/gem1.png").convert_alpha(),
    "pink": pg.image.load("gfx/gem2.png").convert_alpha(),
    "blue": pg.image.load("gfx/gem3.png").convert_alpha(),
    "green": pg.image.load("gfx/gem4.png").convert_alpha()
}
TITLE_FONT = pg.font.SysFont("comicsansms",40)
TEXT_FONT = pg.font.SysFont("lucidaconsole",16)
TITLE = TITLE_FONT.render("Sugar Smash", True, PALETTE["yellow"])

#classes

class CandyPiece:

    def __init__(self,x,y,type):
        self.type = type
        self.x = x
        self.y = y
    
    def draw(self, surface):
        surface.blit(JEWELS[self.type],(self.x+4,self.y+4))

#create objects
clock = pg.time.Clock()
pieces = []
x = 50
y = 60
while (x + 40 < 260):
    while (y + 40 < 430):
        type = TYPES[random.randint(0,4)]
        pieces.append(CandyPiece(x,y,type))
        y += 40
    y = 60
    x += 40
print(len(pieces))

#main loop
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    (x,y) = pg.mouse.get_pos()

    screen.fill(PALETTE["teal"])
    pg.draw.rect(screen, PALETTE["yellow"], pg.Rect(50,50,200,380))
    for piece in pieces:
        piece.draw(screen)
    mouseLabel = TEXT_FONT.render(f"mouse: ({x}, {y})", True, PALETTE["red"], PALETTE["yellow"])
    screen.blit(mouseLabel, (15,455))
    screen.blit(TITLE, (20,-10))

    clock.tick(60)
    pg.display.update()