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
clock = pg.time.Clock()

#main loop
running = True
while running:
    for event in pg.event.get():
        #print(event)
        """
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_a:
                print("A pressed!")
        if event.type == pg.KEYUP and event.key == pg.K_a:
            print("A released!")
        """
        if event.type == pg.QUIT:
            running = False
    """
    keys = pg.key.get_pressed()
    if keys[pg.K_s]:
        print("S currently down!")
    """
    screen.fill(PALETTE["teal"])
    pg.draw.rect(screen, PALETTE["yellow"], pg.Rect(50,50,200,400))
    #pg.display.set_caption(str(clock.get_fps()))
    clock.tick(60)
    pg.display.update()