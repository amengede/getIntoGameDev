from config import *
from systems.renderer import Renderer

class Game:
    """
        Calls high level control functions (handle input, draw scene etc)
    """

    def __init__(self):
        self.screen_width = 640
        self.screen_height = 480
        self.renderer = Renderer(self.screen_width, self.screen_height)
        self.clock = pg.time.Clock()
    
    def play(self):

        running = True
        while (running):
            #events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
            
            self.renderer.update()

            #timing
            self.clock.tick()
            framerate = int(self.clock.get_fps())
            pg.display.set_caption(f"Running at {framerate} fps.")
        self.quit()
    
    def quit(self):
        pg.quit()