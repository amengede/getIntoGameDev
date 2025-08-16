import pygame as pg
import numpy as np

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

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
              x: int, y: int, w: int, h: int,
              color: np.uint32) -> None:

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

pg.init()
screen_surface, screen_pixels = make_screen(SCREEN_SIZE)

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
            running = False
        
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                print("Left click")
    
    keys = pg.key.get_pressed()
    if keys[pg.K_ESCAPE]:
        running = False
    
    screen_surface.lock()

    clear(screen_pixels, PURPLE)

    # draw ball
    draw_rect(screen_pixels, 400, 300, 5, 5, GREEN)
    
    blit(title, screen_pixels, (200, 100))
    blit(subtitle, screen_pixels, (100, 200))

    screen_surface.unlock()
    
    pg.display.update()
