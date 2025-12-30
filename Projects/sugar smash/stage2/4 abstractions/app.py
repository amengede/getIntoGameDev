from config import *
import board

class App:

    TITLE_FONT = pg.font.SysFont("comicsansms",40)
    TEXT_FONT = pg.font.SysFont("lucidaconsole",16)

    def __init__(self):
        self.clock = pg.time.Clock()
        self.board = board.GameBoard(50,50)
        self.title = App.TITLE_FONT.render("Sugar Smash", True, PALETTE["yellow"])

    def mainLoop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
        (x,y) = pg.mouse.get_pos()

        SCREEN.fill(PALETTE["teal"])
        self.board.draw(SCREEN)
        mouseLabel = App.TEXT_FONT.render(f"mouse: ({x}, {y})", True, PALETTE["red"], PALETTE["yellow"])
        SCREEN.blit(mouseLabel, (15,455))
        SCREEN.blit(self.title, (20,-10))
        
        self.clock.tick(60)
        pg.display.update()
        return True