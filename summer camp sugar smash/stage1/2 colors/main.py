import pygame as pg
pg.init()

# global variables
SCREEN_SIZE = (300,600)
PALETTE = {
    "teal":(41,127,135),
    "yellow":(246,209,103),
    "light-yellow":(255,247,174),
    "red":(223,46,46)
}

#create objects
screen = pg.display.set_mode(SCREEN_SIZE)

#main loop
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    screen.fill(PALETTE["teal"])
    pg.draw.rect(screen, PALETTE["yellow"], pg.Rect(50,50,200,400))
    pg.display.update()