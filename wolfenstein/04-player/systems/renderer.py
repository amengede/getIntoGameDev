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

@njit()
def draw_rectangle(color_buffer: np.ndarray, color: int,
                   top_left: tuple[int], size: tuple[int]) -> None:
    
    x1, y1 = top_left
    w, h = size
    
    for x in range(x1, x1 + w):
        color_buffer[x][y1:y1 + h] = color

@njit()
def line_dda(color_buffer: np.ndarray, 
             x1: int, y1: int, x2: int, y2: int, 
             color: int) -> None:
    
    dx = int32(x2 - x1)
    dy = int32(y2 - y1)
    
    steps = max(np.abs(dx), np.abs(dy))

    x_increment = float32(dx / steps)
    y_increment = float32(dy / steps)

    x = x1
    y = y1
    for _ in range(steps):
        color_buffer[int32(x)][int32(y)] = color
        x += x_increment
        y += y_increment

class Renderer:
    """
        Responsible for drawing scenes
    """

    def __init__(self, width: int, height: int, 
                 game_map: np.ndarray, player: np.ndarray):

        pg.init()
        self.screen_surface = pg.display.set_mode((width, height))
        self.screen_pixels = pg.surfarray.array2d(self.screen_surface)

        colors = (
            self.screen_surface.map_rgb(  0,   0,   0), #black
            self.screen_surface.map_rgb(255, 255, 255), #white
            self.screen_surface.map_rgb( 56,  56,  56), #ceiling
            self.screen_surface.map_rgb(112, 112, 112), #floor
            self.screen_surface.map_rgb(  0,   0, 255), #color 1
            self.screen_surface.map_rgb(255, 255,   0), #color 2
            self.screen_surface.map_rgb(  0, 255, 255), #color 3
            self.screen_surface.map_rgb(  0, 255,   0), #color 4
            self.screen_surface.map_rgb(255,   0, 255), #color 5
            self.screen_surface.map_rgb(255,   0,   0), #color 6
            )

        self.states = (
            GameRenderer(width, height, game_map, colors, self.screen_pixels, player),
            MapRenderer(width, height, game_map, colors, self.screen_pixels, player)
        )
        self.state_index = 0
        self.state = self.states[self.state_index]
    
    def toggle_draw_mode(self):

        # toggles: 0 -> 1, 1 -> 0
        self.state_index = (self.state_index + 1) % 2
        self.state = self.states[self.state_index]
    
    def update(self):
        """
            Draws a frame
        """

        self.state.update()
            
        pg.surfarray.blit_array(self.screen_surface, self.screen_pixels)
        pg.display.flip()

class GameRenderer:

    def __init__(self, width: int, height: int, 
                 game_map: np.ndarray, colors: tuple[int], 
                 screen_pixels: np.ndarray,
                 player: np.ndarray):

        self.width = width
        self.height = height
        self.screen_pixels = screen_pixels
        self.colors = colors
        self.player = player
    
    def update(self):
        """
            Draws a frame
        """

        #ceiling
        top_left = (0, 0)
        size = (self.width, int(self.height / 2))
        draw_rectangle(self.screen_pixels, self.colors[2], top_left, size)

        #floor
        top_left = (0, int(self.height / 2))
        draw_rectangle(self.screen_pixels, self.colors[3], top_left, size)

class MapRenderer:

    def __init__(self, width: int, height: int, 
                 game_map: np.ndarray, colors: tuple[int], 
                 screen_pixels: np.ndarray, player: np.ndarray):

        self.width = width
        self.height = height
        self.screen_pixels = screen_pixels
        self.colors = colors
        
        self.map_width = len(game_map)
        self.map_height = len(game_map[0])
        self.map = game_map
        self.grid_size = (
            int(self.width / self.map_width), 
            int(self.height / self.map_height))
        
        self.player = player
        
    def update(self):
        """
            Draws a frame
        """

        clear_screen(self.screen_pixels, self.colors[0])

        # player
        color = self.colors[1]
        size = (8, 8)
        top_left = (
            int(self.player[0] * self.grid_size[0] - 4), 
            int(self.player[1] * self.grid_size[1] - 4))
        draw_rectangle(self.screen_pixels, color, top_left, size)

        for x in range(self.map_width):
            for y in range(self.map_height):
                tile = self.map[x][y]
                if tile == 0:
                    continue

                color = self.colors[tile + 3]
                top_left = (x * self.grid_size[0], y * self.grid_size[1])
                draw_rectangle(self.screen_pixels, color, top_left, self.grid_size)

        for x in range(0, self.width, self.grid_size[0]):
            draw_vertical_line(self.screen_pixels, self.colors[1], x, 0, self.height)
        
        for y in range(0, self.height, self.grid_size[1]):
            draw_horizontal_line(self.screen_pixels, self.colors[1], 0, self.width, y)
        
        # forwards
        x1 = self.player[0] * self.grid_size[0]
        y1 = self.player[1] * self.grid_size[1]
        forwards_x, forwards_y = rotate(16, 0, self.player[2])
        x2 = self.player[0] * self.grid_size[0] + forwards_x
        y2 = self.player[1] * self.grid_size[1] + forwards_y
        color = self.colors[6]
        line_dda(self.screen_pixels, x1, y1, x2, y2, color)

        # right
        right_x, right_y = rotate(0, -16, self.player[2])
        x2 = self.player[0] * self.grid_size[0] + right_x
        y2 = self.player[1] * self.grid_size[1] + right_y
        color = self.colors[7]
        line_dda(self.screen_pixels, x1, y1, x2, y2, color)