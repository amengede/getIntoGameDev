from config import *
import board
import button

class App:

    TITLE_FONT = pg.font.SysFont("comicsansms",40)
    TEXT_FONT = pg.font.SysFont("lucidaconsole",16)
    CONTINUE = 0
    NEWGAME = 1
    EXIT = 2

    def __init__(self):
        self.clock = pg.time.Clock()
        self.board = board.GameBoard(50,50)
        self.title = App.TITLE_FONT.render("Sugar Smash", True, PALETTE["yellow"])
        self.score = 0
        self.newGameButton = button.Button(pg.Rect(100,500,100,50), "New Game", PALETTE["light-yellow"],PALETTE["yellow"])
        

    def mainLoop(self):
        #events
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                self.board.handleMouseClick()
                clicked = self.newGameButton.handleMouseClick()
                if clicked:
                    return App.NEWGAME
            if event.type == pg.QUIT:
                return App.EXIT
        (x,y) = pg.mouse.get_pos()
        self.score += self.board.update()
        self.newGameButton.handleMouse()

        #draw screen
        SCREEN.fill(PALETTE["teal"])
        self.board.draw(SCREEN)
        scoreLabel = App.TEXT_FONT.render(f"Points: {self.score}", True, PALETTE["red"], PALETTE["yellow"])
        SCREEN.blit(scoreLabel, (15,455))
        SCREEN.blit(self.title, (20,-10))
        self.newGameButton.draw(SCREEN)
        
        #misc stuff
        self.clock.tick(60)
        pg.display.update()
        return App.CONTINUE