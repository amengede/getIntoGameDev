import pygame as pg

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

pg.init()
screen_surface = pg.display.set_mode(SCREEN_SIZE)
screen_pixels = pg.surfarray.pixels2d(screen_surface)

pixel_format = screen_pixels.dtype
dimensions = screen_pixels.shape
shifts = screen_surface.get_shifts()

PURPLE = 64 << shifts[0] | 64 << shifts[2]
GREEN = 128 << shifts[1]

font = pg.font.Font(size=64)
title = font.render("Pong", False, (0,128,0))
title_pixels = pg.surfarray.pixels2d(title)
subtitle = font.render("Press space to begin", False, (0,128,0))
subtitle_pixels = pg.surfarray.pixels2d(subtitle)

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
    
    mouse_pos = pg.mouse.get_pos()
    #print(mouse_pos)
    
    screen_surface.lock()

    # clear screen
    screen_pixels &= 0
    screen_pixels |= PURPLE

    # draw 5x5 green splotch at center
    for x in range(-2,3):
        for y in range(-2, 3):
            screen_pixels[400 + x, 300 + y] = GREEN
    
    # draw title
    for x in range(title_pixels.shape[0]):
        for y in range(title_pixels.shape[1]):
            if title_pixels[x,y]:
                screen_pixels[200 + x, 100 + y] = GREEN
    
    # draw subtitle
    for x in range(subtitle_pixels.shape[0]):
        for y in range(subtitle_pixels.shape[1]):
            if subtitle_pixels[x,y]:
                screen_pixels[100 + x, 200 + y] = GREEN

    screen_surface.unlock()
    
    pg.display.update()
