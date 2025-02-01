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
        self.load_map("level.txt")

        # make systems
        self.renderer = Renderer(self.screen_width, self.screen_height, 
                                 self.map, self.player)
        self.clock = pg.time.Clock()
        pg.mouse.set_visible(False)
    
    def load_map(self, filename: str) -> None:

        with open(filename, "r") as file:
            line = file.readline()

            while line:
                line = line.strip()
                words: list[str] = line.split(" ")

                if words[0] == "size":
                    self.map = self.allocate_map(words)
                
                if words[0] == "map":
                    self.fill_map(file)

                if words[0] == "player":
                    self.player = self.make_player(words)
                
                line = file.readline()
    
    def allocate_map(self, words: list[str]) -> np.ndarray:
        
        w = int(words[1])
        h = int(words[2])
        return np.zeros((w,h), dtype = np.uint8)
    
    def fill_map(self, file) -> np.ndarray:
        
        line = file.readline()
        y = 0

        while line:
            line = line.strip()
            words: list[str] = line.split(" ")

            if words[0] == "end":
                return
            
            x = 0
            for word in words:
                self.map[x][y] = int(word)
                x += 1
            y += 1

            line = file.readline()
    
    def make_player(self, words: list[str]) -> np.ndarray:
        
        x = int(words[1])
        y = int(words[2])
        theta = float(words[3])
        return np.array((x,y,theta), dtype = np.float32)

    
    def play(self):

        running = True
        self.frametime = 0.0
        while (running):
            #events
            for event in pg.event.get():

                if (event.type == pg.KEYDOWN):
                    if (event.key == pg.K_TAB):
                        self.renderer.toggle_draw_mode()
                    if (event.key == pg.K_ESCAPE):
                        running = False
            
            self.handle_keys()
            self.handle_mouse()
            
            self.renderer.update()

            #timing
            self.clock.tick()
            framerate = int(self.clock.get_fps())
            self.frametime = 1000.0 / max(framerate, 1.0)
            pg.display.set_caption(f"Running at {framerate} fps.")
        self.quit()
    
    def handle_keys(self) -> None:

        forwards_x, forwards_y = rotate(1, 0, self.player[2])
        right_x, right_y = rotate(0, -1, self.player[2])
        velocity_x = 0.0
        velocity_y = 0.0

        keys = pg.key.get_pressed()
        speed = 0.05 * self.frametime / 16.67
        
        if keys[pg.K_a]:
            velocity_x -= speed * right_x
            velocity_y -= speed * right_y
        if keys[pg.K_d]:
            velocity_x += speed * right_x
            velocity_y += speed * right_y
        if keys[pg.K_w]:
            velocity_x += speed * forwards_x
            velocity_y += speed * forwards_y
        if keys[pg.K_s]:
            velocity_x -= speed * forwards_x
            velocity_y -= speed * forwards_y
        
        magnitude = np.sqrt(velocity_x * velocity_x + velocity_y * velocity_y)

        if magnitude == 0:
            return
        
        dx = 0.25 * velocity_x / magnitude
        dy = 0.25 * velocity_y / magnitude
        
        if self.can_move(self.player[0], self.player[1], dx, 0.0):
            self.player[0] += velocity_x
        
        if self.can_move(self.player[0], self.player[1], 0.0, dy):
            self.player[1] += velocity_y
    
    def can_move(self, x: float, y: float, dx: float, dy: float) -> bool:

        x_test = int(x + dx)
        y_test = int(y + dy)

        return self.map[x_test][y_test] == 0
    
    def handle_mouse(self) -> None:
        
        current_pos = pg.mouse.get_pos()
        speed = 0.1

        dx = current_pos[0] - self.screen_width / 2
        if abs(dx) > 0:

            self.player[2] += speed * dx
            if self.player[2] > 360:
                self.player[2] -= 360
            if self.player[2] < 0:
                self.player[2] += 360

            pg.mouse.set_pos(self.screen_width / 2, self.screen_height / 2)
    
    def quit(self):
        pg.quit()