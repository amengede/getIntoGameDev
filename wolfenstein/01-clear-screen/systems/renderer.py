from config import *

def clear_screen(color_buffer: np.ndarray, color: int) -> None:
    color_buffer &= 0
    color_buffer |= color

class Renderer:
    """
        Responsible for drawing scenes
    """

    def __init__(self, width: int, height: int):
        """
            Initialize a rendering engine.
            
                Parameters:
                    width (int): width of screen
                    height (int): height of screen
        """

        pg.init()
        self.screen_surface = pg.display.set_mode((width, height))
        self.screen_pixels = pg.surfarray.array2d(self.screen_surface)

        self.colors = (
            self.screen_surface.map_rgb(16, 16, 16), 
            self.screen_surface.map_rgb(128, 128, 128))
    
    def update(self):
        """
            Draws a frame
        """

        clear_screen(self.screen_pixels, self.colors[0])
            
        pg.surfarray.blit_array(self.screen_surface, self.screen_pixels)
        pg.display.flip()