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

print("Got direct pixel access")
print(f"Pixel storage format: {pixel_format}")
print(f"Bit shifts: R: {shifts[0]}, G: {shifts[1]}, B: {shifts[2]}, A: {shifts[3]}")

PURPLE = 64 << shifts[0] | 64 << shifts[2]
GREEN = 128 << shifts[1]

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

    screen_surface.unlock()
    pg.display.update()
