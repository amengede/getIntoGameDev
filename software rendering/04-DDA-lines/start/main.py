from config import *
import backend
################################## View #######################################
#region
@njit((uint8[:],))
def map_to_uint32(color: np.ndarray) -> int:
    r,g,b,a = color
    return uint32((r << 24) + (g << 16) + (b << 8) + a)

@njit((uint32[:], uint32))
def clear_screen(color_buffer: np.ndarray, color: int) -> None:
    color_buffer &= uint32(0)
    color_buffer |= color

@njit((uint32[:], uint32, uint32, uint32, uint32))
def set_pixel(color_buffer: np.ndarray, x: int, y: int, 
              color: int, height: int) -> None:
    
    color_buffer[x * height + y] = color

@njit((uint32[:], uint32, uint32, uint32, uint32, uint32))
def horizontal_line(color_buffer: np.ndarray, x1: int, x2: int, y: int, 
                    color: int, height: int) -> None:
    
    x_left = min(x1, x2)
    x_right = max(x1, x2)

    for x in range(x_left, x_right):
        set_pixel(color_buffer, x, y, color, height)

@njit((uint32[:], uint32, uint32, uint32, uint32, uint32))
def vertical_line(color_buffer: np.ndarray, x: int, y1: int, y2: int, 
                    color: int, height: int) -> None:
    
    y_top = min(y1, y2)
    y_bottom = max(y1, y2)

    color_buffer[x * height + y_top : x * height + y_bottom] = color

class EngineFrontend:
    """
        Responsible for drawing scenes
    """

    def __init__(self, width, height):
        """
            Initialize a rendering engine.
            
                Parameters:
                    width (int): width of screen
                    height (int): height of screen
        """
        self.screenWidth = width
        self.screenHeight = height

        self.backend = backend.EngineBackend(width, height)
        
        self.color_buffer = self.backend.get_color_buffer()

        self.colors = (
            map_to_uint32(np.array([16, 16, 16, 255], dtype = np.uint8)), 
            map_to_uint32(np.array([128, 128, 128, 255], dtype = np.uint8)))
    
    def draw_frame(self):
        """
            Draws a frame
        """

        clear_screen(self.color_buffer, self.colors[0])

        for y in range(0, self.screenHeight, 32):
            x1 = 0
            x2 = self.screenWidth
            horizontal_line(self.color_buffer, x1, x2, y, self.colors[1], self.screenHeight)

        for x in range(0, self.screenWidth, 32):
            y1 = 0
            y2 = self.screenHeight
            vertical_line(self.color_buffer, x, y1, y2, self.colors[1], self.screenHeight)
            
        self.backend.present()
    
    def destroy(self):
        """
            Free any allocated memory
        """

        self.backend.destroy()
#endregion
################################## Control ####################################
#region
class App:
    """
        Calls high level control functions (handle input, draw scene etc)
    """

    def __init__(self):
        self.screenWidth = 640
        self.screenHeight = 480
        self.renderer = EngineFrontend(self.screenWidth, self.screenHeight)
        self.clock = pg.time.Clock()
        self.mainLoop()
    
    def mainLoop(self):

        running = True
        while (running):
            #events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
            
            self.renderer.draw_frame()

            #timing
            self.clock.tick()
            framerate = int(self.clock.get_fps())
            pg.display.set_caption(f"Running at {framerate} fps.")
        self.quit()
    
    def quit(self):
        self.renderer.destroy()
        pg.quit()
#endregion
###############################################################################
myApp = App()