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
PIECE_SIZE = 40

#classes

class CandyPiece:

    def __init__(self,x,y,type):
        self.type = type
        self.x = x
        self.y = y
    
    def draw(self, surface):
        surface.blit(JEWELS[self.type],(self.x+4,self.y+4))

class GameBoard:

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.width = 200
        self.height = 380
        self.surface = pg.Surface((self.width,self.height))
        self.numRows = self.height//PIECE_SIZE
        self.numCols = self.width//PIECE_SIZE
        self.pieces = []
        self.reset()
        self.populate()
    
    def reset(self):
        for row in range(self.numRows):
            self.pieces.append([])
            for column in range(self.numCols):
                self.pieces[row].append(None)
    
    def populate(self):
        for row in range(self.numRows):
            for column in range(self.numCols):
                x = column*PIECE_SIZE
                y = row*PIECE_SIZE
                type = TYPES[random.randint(0,4)]
                self.pieces[row][column] = CandyPiece(x,y,type)
                
    def draw(self, surface):
        self.surface.fill(PALETTE["yellow"])
        for row in range(self.numRows):
            for column in range(self.numCols):
                if self.pieces[row][column] != None:
                    self.pieces[row][column].draw(self.surface)
        surface.blit(self.surface,(self.x,self.y))

#create objects
clock = pg.time.Clock()
board = GameBoard(50,50)

#main loop
running = True
while running:
    for event in pg.event.get():
        #print(event)
        """
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_a:
                print("A pressed!")
        if event.type == pg.KEYUP and event.key == pg.K_a:
            print("A released!")
        """
        if event.type == pg.QUIT:
            running = False
    """
    keys = pg.key.get_pressed()
    if keys[pg.K_s]:
        print("S currently down!")
    """
    (x,y) = pg.mouse.get_pos()

    screen.fill(PALETTE["teal"])
    board.draw(screen)
    mouseLabel = TEXT_FONT.render(f"mouse: ({x}, {y})", True, PALETTE["red"], PALETTE["yellow"])
    screen.blit(mouseLabel, (15,455))
    #targetSurface.blit(sourceSurface, upperLeft)
    screen.blit(TITLE, (20,-10))

    #pg.display.set_caption(str(clock.get_fps()))
    clock.tick(60)
    pg.display.update()