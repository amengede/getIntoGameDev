from config import *
from systems.renderer import Renderer

class Game:
    """
        Calls high level control functions (handle input, draw scene etc)
    """

    def __init__(self):

        # screen size
        self.screen_width = 640
        self.screen_height = 480

        # load map
        self.map = self.load_map("level.txt")

        # make systems
        self.renderer = Renderer(self.screen_width, self.screen_height, self.map)
        self.clock = pg.time.Clock()
    
    def load_map(self, filename: str) -> np.ndarray:

        with open(filename, "r") as file:
            line = file.readline()

            while line:
                line = line.strip()
                words: list[str] = line.split(" ")

                if words[0] == "size":
                    game_map = self.allocate_map(words)
                
                if words[0] == "map":
                    self.fill_map(file, game_map)
                line = file.readline()
        
        return game_map
    
    def allocate_map(self, words: list[str]) -> np.ndarray:
        
        w = int(words[1])
        h = int(words[2])
        return np.zeros((w,h), dtype = np.uint8)
    
    def fill_map(self, file, game_map: np.ndarray) -> np.ndarray:
        
        line = file.readline()
        y = 0

        while line:
            line = line.strip()
            words: list[str] = line.split(" ")

            if words[0] == "end":
                return
            
            x = 0
            for word in words:
                game_map[x][y] = int(word)
                x += 1
            y += 1

            line = file.readline()

    
    def play(self):

        running = True
        while (running):
            #events
            for event in pg.event.get():

                if (event.type == pg.KEYDOWN and event.key == pg.K_TAB):
                    self.renderer.toggle_draw_mode()
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