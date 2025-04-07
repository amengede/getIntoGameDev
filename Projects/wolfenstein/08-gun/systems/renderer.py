from config import *

#---- Constants ----#
#region
TEXTURE_FILENAMES = (
    "img/comp1_1.jpg",
    "img/tech01_2.jpg",
    "img/tech01_7.jpg",
    "img/tech08_1.jpg",
    "img/tech09_3.jpg",
    "img/twall2_6.jpg",)

GUN_FILENAMES = (
    "img/BBUSA.png",
    "img/BBUSB.png",
    "img/BBUSC.png",
    "img/BBUSD.png",
    "img/BBUSE.png",
    "img/BBUSF.png",
    "img/BBUSG.png",
    "img/BBUSH.png",
    "img/BBUSI.png",
)
#endregion
#---- Helper Functions ----#
#region
def load_texture(filename: str) -> np.ndarray:

    surface = pg.image.load(filename).convert()
    array = pg.surfarray.array2d(surface)
    return array

def load_image(filename: str) -> pg.Surface:

    return pg.image.load(filename).convert_alpha()

def clear_screen(color_buffer: np.ndarray, color: int) -> None:
    color_buffer &= 0
    color_buffer |= color

@njit()
def draw_vertical_line(color_buffer: np.ndarray, color: int, 
                  x: int, y1: int, y2: int) -> None:

    color_buffer[x][y1:y2] = color

@njit()
def draw_vertical_line_textured(color_buffer: np.ndarray, 
                texture: np.ndarray, tex_x: int,
                x: int, y1: int, y2: int, wall_height: int, screen_height: int) -> None:
    true_wall_top = int(0.5 * screen_height - wall_height)
    #print(f"true wall top: {true_wall_top}, actual wall top: {y1}")
    clipping = max(0, -true_wall_top)
    #print(f"clipping: {clipping}")
    dv = 256.0 / wall_height
    #print(f"dv: {dv}")
    v = clipping * dv
    y = y1

    while y < y2:
        tex_y = min(511, int(v))
        color_buffer[x][y] = texture[tex_x][tex_y]
        v = v + dv
        y += 1

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

@njit()
def get_ray(x: int, w: int, 
                       forwards: tuple[float], 
                       right: tuple[float]) -> tuple[float]:
    
    coefficient = (2.0 * x - w) / float(w)

    ray_x = forwards[0] + coefficient * right[0]
    ray_y = forwards[1] + coefficient * right[1]

    return (ray_x, ray_y)

@njit()
def trace(ray: tuple[float], position: tuple[float], 
          game_map: np.ndarray) -> tuple[float, int, int]:
    
    # trace
    map_x = int(position[0])
    map_y = int(position[1])
    dist_x = 1 / max(abs(ray[0]), 1e-10)
    dist_y = 1 / max(abs(ray[1]), 1e-10)
    proportion_from_left = position[0] - map_x
    step_x = int(np.sign(ray[0]))
    t_x = proportion_from_left * dist_x if step_x < 0 else (1.0 - proportion_from_left) * dist_x
    proportion_from_bottom = position[1] - map_y
    step_y = int(np.sign(ray[1]))
    t_y = proportion_from_bottom * dist_y if step_y < 0 else (1.0 - proportion_from_bottom) * dist_y

    tile = game_map[map_x][map_y]
    side = 0

    while tile == 0:

        # step forwards
        if t_x < t_y:
            t_x += dist_x
            map_x += step_x
            side = 0
        else:
            t_y += dist_y
            map_y += step_y
            side = 1
        
        tile = game_map[map_x][map_y]

    distance = t_x - dist_x if side == 0 else t_y - dist_y
    
    return (distance, tile, side)

@njit()
def raycast_scene(camera: np.ndarray, width: int, height: int, game_map: np.ndarray, color_buffer: np.ndarray, colors: tuple[int], textures: tuple[np.ndarray]):
    
    forwards = rotate(1, 0, camera[2])
    right = rotate(0, -1, camera[2])
    for x in range(width):

        ray = get_ray(x, width, forwards, right)

        distance, tile, side = trace(ray, camera, game_map)

        wall_height = 0.5 * height / distance

        y_top = int(max(0, int(0.5 * height - wall_height)))
        y_bottom = int(min(height - 1, int(0.5 * height + wall_height)))
        texture = textures[tile - 1]

        # exact position along wall where hit occurred
        u = camera[1] + ray[1] * distance if side == 0 else camera[0] + ray[0] * distance
        # in fraction form
        u = u - int(u)

        tex_x = int(u * 512)
        if side == 0 and ray[0] > 0:
            tex_x = 512 - tex_x - 1
        if side == 1 and ray[1] < 0:
            tex_x = 512 - tex_x - 1

        # ceiling
        draw_vertical_line(color_buffer, colors[2], x, 0, y_top)
        # wall
        draw_vertical_line_textured(color_buffer, texture, tex_x, x, y_top, y_bottom, wall_height, color_buffer.shape[1])
        # floor
        draw_vertical_line(color_buffer, colors[3], x, y_bottom, height)
#endregion
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
            self.screen_surface.map_rgb(  0,   0, 128), #color 1 (dark)
            self.screen_surface.map_rgb(128, 128,   0), #color 2 (dark)
            self.screen_surface.map_rgb(  0, 128, 128), #color 3 (dark)
            self.screen_surface.map_rgb(  0, 128,   0), #color 4 (dark)
            self.screen_surface.map_rgb(128,   0, 128), #color 5 (dark)
            self.screen_surface.map_rgb(128,   0,   0), #color 6 (dark)
            )
        
        textures = [load_texture(filename) for filename in TEXTURE_FILENAMES]

        self.event_queue = []
        self.observers: list[list[int]] = []

        self.states = (
            GameRenderer(width, height, game_map, colors, textures, 
                         self.screen_pixels, player, self.screen_surface,
                         self.event_queue, self.observers),
            MapRenderer(width, height, game_map, colors, 
                        self.screen_pixels, player, self.screen_surface,
                        self.event_queue, self.observers)
        )
        self.state_index = 0
        self.state = self.states[self.state_index]
    
    def toggle_draw_mode(self):

        # toggles: 0 -> 1, 1 -> 0
        self.state_index = (self.state_index + 1) % 2
        self.state = self.states[self.state_index]
    
    def update(self, frametime: float):
        """
            Draws a frame
        """

        self.state.update(frametime)
        self.event_queue.clear()
        pg.display.flip()

class GameRenderer:

    def __init__(self, width: int, height: int, 
                 game_map: np.ndarray, 
                 colors: tuple[int], 
                 textures: tuple[np.ndarray],
                 screen_pixels: np.ndarray,
                 player: np.ndarray,
                 screen: pg.Surface,
                 event_queue: list[int],
                 observers: list[list[int]]):

        self.width = width
        self.height = height
        self.screen_pixels = screen_pixels
        self.textures = textures
        self.colors = colors
        self.player = player
        self.map = game_map
        self.gun_frames = [load_image(filename) for filename in GUN_FILENAMES]
        self.screen = screen

        self.event_queue = event_queue

        self.player_walking = False
        self.player_walking_t = 0.0
        self.player_walking_offset = 0.0

        self.player_shooting = False
        self.gun_frame_index = 0
        self.gun_frame_time = 0

        self.observers = observers
    
    def update(self, frametime: float):
        """
            Draws a frame
        """

        for event in self.event_queue:
            if event == MESSAGE_TYPE_PLAYER_WALKING:
                self.player_walking = True
                self.player_walking_t = 0
            elif event == MESSAGE_TYPE_PLAYER_STOP:
                self.player_walking = False
            elif event == MESSAGE_TYPE_PLAYER_SHOOT:
                self.player_shooting = True
                self.gun_frame_index = 1


        raycast_scene(self.player, self.width, self.height, self.map, 
                      self.screen_pixels, self.colors, self.textures)
        pg.surfarray.blit_array(self.screen, self.screen_pixels)
        self.draw_gun(frametime)
    
    def draw_gun(self, frametime: float) -> None:

        ms_per_frame = 75

        if self.player_walking:
            self.player_walking_t += frametime
            self.player_walking_offset = 20.0 * np.sin(0.01 * self.player_walking_t)
        else:
            sign = np.sign(self.player_walking_offset)
            self.player_walking_offset -= sign * 0.1 * frametime
            if (np.sign(self.player_walking_offset) * sign) < 0.0:
                self.player_walking_offset = 0.0
        
        if self.player_shooting:
            self.gun_frame_time += frametime

            if self.gun_frame_time > ms_per_frame:
                self.gun_frame_time -= ms_per_frame
                self.gun_frame_index += 1

            if (self.gun_frame_index >= len(self.gun_frames)):
                self.gun_frame_index = 0
                self.player_shooting = False
                publish(MESSAGE_TYPE_PLAYER_RELOAD, self.observers)

        dest = (320 + self.player_walking_offset, 160)
        self.screen.blit(self.gun_frames[self.gun_frame_index], dest)

class MapRenderer:

    def __init__(self, width: int, height: int, 
                 game_map: np.ndarray, colors: tuple[int], 
                 screen_pixels: np.ndarray, player: np.ndarray,
                 screen: pg.surface, event_queue: list[int],
                 observers: list[list[int]]):

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
        self.screen = screen

        self.event_queue = event_queue

        self.observers = observers
        
    def update(self, frametime: float):
        """
            Draws a frame
        """

        clear_screen(self.screen_pixels, self.colors[0])

        # trace
        map_x = int(self.player[0])
        map_y = int(self.player[1])
        dx, dy = rotate(1, 0, self.player[2])
        dist_x = 1 / abs(dx)
        dist_y = 1 / abs(dy)
        proportion_from_left = self.player[0] - map_x
        t_x = proportion_from_left * dist_x if dx < 0 else (1.0 - proportion_from_left) * dist_x
        step_x = int(np.sign(dx))
        proportion_from_bottom = self.player[1] - map_y
        t_y = proportion_from_bottom * dist_y if dy < 0 else (1.0 - proportion_from_bottom) * dist_y
        step_y = int(np.sign(dy))

        while self.map[map_x][map_y] == 0:

            # draw current square
            color = self.colors[3]
            top_left = (map_x * self.grid_size[0], map_y * self.grid_size[1])
            draw_rectangle(self.screen_pixels, color, top_left, self.grid_size)

            # step forwards
            if t_x < t_y:
                t_x += dist_x
                map_x += step_x
            else:
                t_y += dist_y
                map_y += step_y

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

        pg.surfarray.blit_array(self.screen, self.screen_pixels)