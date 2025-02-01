from config import *

def clear_screen(color_buffer: np.ndarray, color: int) -> None:
    color_buffer &= 0
    color_buffer |= color

def draw_vertical_line(color_buffer: np.ndarray, color: int, 
                  x: int, y1: int, y2: int) -> None:

    color_buffer[x][y1:y2] = color

def draw_horizontal_line(color_buffer: np.ndarray, color: int, 
                  x1: int, x2: int, y: int) -> None:

    for x in range(x1, x2):
        color_buffer[x][y] = color

@njit((int32[:,:], int32, int32, int32, int32, int32))
def draw_rectangle(color_buffer: np.ndarray, color: int,
                   x1: int, y1: int, x2: int, y2: int) -> None:
    
    for x in range(x1, x2):
        color_buffer[x][y1:y2] = color

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
        self.width = width
        self.height = height
        self.screen_surface = pg.display.set_mode((width, height))
        self.screen_pixels = pg.surfarray.array2d(self.screen_surface)

        self.colors = (
            self.screen_surface.map_rgb(0, 0, 0),       #black
            self.screen_surface.map_rgb(255, 255, 255), #white
            self.screen_surface.map_rgb(56, 56, 56),    #ceiling
            self.screen_surface.map_rgb(112, 112, 112), #floor
            )
    
    def update(self):
        """
            Draws a frame
        """

        #ceiling
        draw_rectangle(self.screen_pixels, self.colors[2], 0, 0, self.width, self.height // 2)

        #floor
        draw_rectangle(self.screen_pixels, self.colors[3], 0, self.height // 2, self.width, self.height)

        for x in range(0, self.width, 40):
            draw_vertical_line(self.screen_pixels, self.colors[1], x, 0, self.height)
        
        for y in range(0, self.height, 40):
            draw_horizontal_line(self.screen_pixels, self.colors[1], 0, self.width, y)
            
        pg.surfarray.blit_array(self.screen_surface, self.screen_pixels)
        pg.display.flip()