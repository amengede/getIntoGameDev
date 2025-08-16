import pygame as pg
import numpy as np

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

GAME_MODE_TITLE = 0
GAME_MODE_PLAY = 1
GAME_MODE_QUIT = 2

def make_screen(size: tuple[int]) -> tuple[pg.Surface, np.ndarray]:
    screen_surface = pg.display.set_mode(size)
    screen_pixels = pg.surfarray.pixels2d(screen_surface)

    return screen_surface, screen_pixels

def map_rgb(color: tuple[int], shifts: tuple[int]) -> np.uint32:
    return color[0] << shifts[0] | color[1] << shifts[1] |color[2] << shifts[2]

def make_text(font: pg.Font, text: str, color: np.uint32) -> np.ndarray:
    
    temp_surface = font.render(text, False, (0,128,0))
    temp_pixels = pg.surfarray.pixels2d(temp_surface)
    pixels = np.zeros(temp_pixels.shape, dtype = np.uint32)
    for x in range(temp_pixels.shape[0]):
        for y in range(temp_pixels.shape[1]):
            if temp_pixels[x,y]:
                pixels[x,y] = color
    return pixels

def clear(pixels: np.ndarray, color: np.uint32) -> None:
    pixels &= 0
    pixels |= color

def draw_rect(pixels: np.ndarray,
              rect: list[int],
              color: np.uint32) -> None:

    x, y, w, h = rect
    x_left = max(0, x - w // 2)
    x_right = min(pixels.shape[0] - 1, x + w // 2 + 1)
    y_top = max(0, y - h // 2)
    y_bottom = min(pixels.shape[1] - 1, y + h // 2 + 1)

    for i in range(x_left, x_right):
        for j in range(y_top, y_bottom):
            screen_pixels[i, j] = color

def blit(src: np.ndarray, dst: np.ndarray, dst_offset: tuple[int]) -> None:

    x_left = max(0, dst_offset[0])
    x_right = min(dst.shape[0] - 1, dst_offset[0] + src.shape[0])
    y_top = max(0, dst_offset[1])
    y_bottom = min(dst.shape[1] - 1, dst_offset[1] + src.shape[1])

    for i in range(src.shape[0]):
        x = i + dst_offset[0]
        if x < x_left or x > x_right:
            continue
        for j in range(src.shape[1]):
            y = j + dst_offset[1]
            if y < y_top or y > y_bottom:
                continue
            if src[i,j]:
                dst[x, y] = src[i,j]

def overlaps(rect_a: list[int], rect_b: list[int]) -> bool:

    x_left_a = rect_a[0] - rect_a[2] // 2
    x_right_b = rect_b[0] + rect_b[2] // 2

    if x_left_a > x_right_b:
        return False
    
    x_right_a = rect_a[0] + rect_a[2] // 2
    x_left_b = rect_b[0] - rect_b[2] // 2

    if x_right_a < x_left_b:
        return False
    
    x_top_a = rect_a[1] - rect_a[3] // 2
    x_bottom_b = rect_b[1] + rect_b[3] // 2

    if x_top_a > x_bottom_b:
        return False
    
    x_bottom_a = rect_a[1] + rect_a[3] // 2
    x_top_b = rect_b[1] - rect_b[3] // 2

    if x_bottom_a < x_top_b:
        return False

    return True
    
def menu_mode(screen_surface: pg.Surface, screen_pixels: np.ndarray) -> int:

    shifts = screen_surface.get_shifts()

    PURPLE = map_rgb((64, 0, 64), shifts)
    GREEN = map_rgb((0, 128, 0), shifts)

    font = pg.font.Font(size=64)
    title = make_text(font, "Pong", GREEN)
    subtitle = make_text(font, "Press space to begin", GREEN)

    running = True
    while running:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return GAME_MODE_QUIT
        
        keys = pg.key.get_just_pressed()
        if keys[pg.K_ESCAPE]:
            return GAME_MODE_QUIT
        
        if keys[pg.K_SPACE]:
            return GAME_MODE_PLAY
        
        screen_surface.lock()

        clear(screen_pixels, PURPLE)

        # draw ball
        draw_rect(screen_pixels, [400, 300, 5, 5], GREEN)
        
        blit(title, screen_pixels, (200, 100))
        blit(subtitle, screen_pixels, (100, 200))

        screen_surface.unlock()
        
        pg.display.update()

def game_mode(screen_surface: pg.Surface, screen_pixels: np.ndarray) -> int:

    shifts = screen_surface.get_shifts()

    BLACK = 0
    WHITE = map_rgb((255, 255, 255), shifts)

    clock = pg.time.Clock()

    ball = [400, 300, 5, 5]
    ball_speed = 6
    theta = np.random.random() * 2 * np.pi
    ball_speed = [int(ball_speed * np.cos(theta)), int(ball_speed * np.sin(theta))]

    paddle_a = [100, 300, 10, 40]
    paddle_b = [700, 300, 10, 40]
    paddle_speed = 8

    running = True
    while running:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return GAME_MODE_QUIT
        
        keys = pg.key.get_just_pressed()
        if keys[pg.K_ESCAPE]:
            return GAME_MODE_TITLE

        update_paddles(paddle_a, paddle_b, paddle_speed)
        
        update_ball(ball, ball_speed, paddle_a, paddle_b)
        
        screen_surface.lock()

        clear(screen_pixels, BLACK)

        draw_rect(screen_pixels, ball, WHITE)
        draw_rect(screen_pixels, paddle_a, WHITE)
        draw_rect(screen_pixels, paddle_b, WHITE)

        screen_surface.unlock()
        
        pg.display.update()
        clock.tick(60)
    
def update_paddles(paddle_a: list[int], paddle_b: list[int], speed: int) -> None:

    keys = pg.key.get_pressed()
    if keys[pg.K_q]:
        paddle_a[1] = max(20, paddle_a[1] - speed)
    if keys[pg.K_a]:
        paddle_a[1] = min(SCREEN_HEIGHT - 20, paddle_a[1] + speed)
    if keys[pg.K_o]:
        paddle_b[1] = max(20, paddle_b[1] - speed)
    if keys[pg.K_l]:
        paddle_b[1] = min(SCREEN_HEIGHT - 20, paddle_b[1] + speed)

def update_ball(ball: list[int], speed: list[int], paddle_a: list[int], paddle_b: list[int]):

    ball[0] += speed[0]
    if overlaps(ball, paddle_a) or overlaps(ball, paddle_b):
        speed[0] *= -1
        ball[0] += speed[0]
    if ball[0] < 0 or ball[0] >= SCREEN_WIDTH:
        speed[0] *= -1
        ball[0] += speed[0]
    ball[1] += speed[1]
    if overlaps(ball, paddle_a) or overlaps(ball, paddle_b):
        speed[1] *= -1
        ball[1] += speed[1]
    if ball[1] < 0 or ball[1] >= SCREEN_HEIGHT:
        speed[1] *= -1
        ball[1] += speed[1]

pg.init()
screen_surface, screen_pixels = make_screen(SCREEN_SIZE)

game_modes = [menu_mode, game_mode]
game_mode = 0

running = True
while running:

    game_mode = game_modes[game_mode](screen_surface, screen_pixels)

    if game_mode == GAME_MODE_QUIT:
        running = False
