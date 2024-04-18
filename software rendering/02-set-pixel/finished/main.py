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
    
    def draw_frame(self):
        """
            Draws a frame
        """

        clear_color = map_to_uint32(np.array([32, 128, 64, 255], dtype = np.uint8))
        clear_screen(self.color_buffer, clear_color)
            
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