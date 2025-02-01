import pygame as pg
pg.init()

# global variables
SCREEN_SIZE = (300,600)
screen = pg.display.set_mode(SCREEN_SIZE)
PALETTE = {
    "teal":(41,127,135),
    "yellow":(246,209,103),
    "light-yellow":(255,247,174),
    "red":(223,46,46)
}
JEWELS = {
    "red": pg.image.load("gfx/gem.png").convert_alpha(),
    "orange": pg.image.load("gfx/gem1.png").convert_alpha(),
    "pink": pg.image.load("gfx/gem2.png").convert_alpha(),
    "blue": pg.image.load("gfx/gem3.png").convert_alpha(),
    "green": pg.image.load("gfx/gem4.png").convert_alpha()
}
#print(pg.font.get_fonts())
TITLE_FONT = pg.font.SysFont("comicsansms",40)
TEXT_FONT = pg.font.SysFont("lucidaconsole",16)
#render(string, antialias, color, background = None) -> Surface
TITLE = TITLE_FONT.render("Sugar Smash", True, PALETTE["yellow"])
#create objects
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
    (x,y) = pg.mouse.get_pos()

    screen.fill(PALETTE["teal"])
    pg.draw.rect(screen, PALETTE["yellow"], pg.Rect(50,50,200,380))
    mouseLabel = TEXT_FONT.render(f"mouse: ({x}, {y})", True, PALETTE["red"], PALETTE["yellow"])
    screen.blit(mouseLabel, (15,455))
    #targetSurface.blit(sourceSurface, upperLeft)
    screen.blit(TITLE, (20,-10))

    jewelTop = 60
    while (jewelTop + 40 < 430):
        screen.blit(JEWELS["red"], (60,jewelTop))
        screen.blit(JEWELS["orange"], (100,jewelTop))
        screen.blit(JEWELS["pink"], (140,jewelTop))
        screen.blit(JEWELS["blue"], (180,jewelTop))
        screen.blit(JEWELS["green"], (220,jewelTop))
        jewelTop += 40

    #pg.display.set_caption(str(clock.get_fps()))
    clock.tick(60)
    pg.display.update()