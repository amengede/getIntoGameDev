import pygame as pg

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

PURPLE = (64, 0, 64)

pg.init()
screen_surface = pg.display.set_mode(SCREEN_SIZE)

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
    
    screen_surface.fill(PURPLE)
    pg.display.update()
