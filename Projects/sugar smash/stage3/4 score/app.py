from config import *
import board

class App:

    TITLE_FONT = pg.font.SysFont("comicsansms",40)
    TEXT_FONT = pg.font.SysFont("lucidaconsole",16)

    def __init__(self):
        self.clock = pg.time.Clock()
        self.board = board.GameBoard(50,50)
        self.title = App.TITLE_FONT.render("Sugar Smash", True, PALETTE["yellow"])
        self.score = 0

    def mainLoop(self):
        #events
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                self.board.handleMouseClick()
            if event.type == pg.QUIT:
                return False
        (x,y) = pg.mouse.get_pos()
        self.score += self.board.update()
        if self.board.hasMouse(x,y):
            (row,column) = self.board.cartesianToGrid(x,y)
        else:
            (row,column) = (-1,-1)

        #draw screen
        SCREEN.fill(PALETTE["teal"])
        self.board.draw(SCREEN)
        scoreLabel = App.TEXT_FONT.render(f"Points: {self.score}", True, PALETTE["red"], PALETTE["yellow"])
        SCREEN.blit(scoreLabel, (15,455))
        SCREEN.blit(self.title, (20,-10))
        
        #misc stuff
        self.clock.tick(60)
        pg.display.update()
        return True