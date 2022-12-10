import pygame as pg
import numpy as np

BLOCK_TYPE_GROUND = 1
BLOCK_TYPE_MUD = 2
BLOCK_TYPE_DEEP_MUD = 4
BLOCK_TYPE_RESTRICTED = np.infty

BACKGROUND_COLOR = (64, 64, 192)
SCREEN_SIZE = (800,600)

COLORS = {
    BLOCK_TYPE_GROUND: (32, 192, 32),
    BLOCK_TYPE_MUD: (128, 128, 32),
    BLOCK_TYPE_DEEP_MUD: (64, 64, 32),
    BLOCK_TYPE_RESTRICTED: (255, 0, 0)
}

BLACK = (0,0,0)

pg.init()
FONT = pg.font.SysFont("arial", 32)

screen_surface = pg.display.set_mode(SCREEN_SIZE)

blocks = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 2, 2, 2, 2, 1, 1, 1, 1],
    [1, 1, 2, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 2, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 4, 4, 4, 4, 4, 4, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

#----    Pathfinding Stuff Here    ----#
start_pos = (7,1)
end_pos = (1,4)
#--------------------------------------#

block_width = SCREEN_SIZE[0] / len(blocks[0])
block_height = SCREEN_SIZE[1] / len(blocks)
block_rect = pg.Rect(0, 0, block_width,  block_height)

running = True
while running:

    for event in pg.event.get():

        if event.type == pg.QUIT:
            running = False
    
    screen_surface.fill(BACKGROUND_COLOR)

    for i,row in enumerate(blocks):
        for j,cost in enumerate(row):
            temp_rect = block_rect.move(j * block_width, i * block_height)
            screen_surface.fill(
                COLORS[cost], 
                temp_rect
            )
            temp_surface = FONT.render(
                str(cost), 
                False,
                BLACK
            )
            screen_surface.blit(temp_surface, temp_rect)
            pg.draw.rect(screen_surface, BLACK, temp_rect, width=2)
    
    i,j = start_pos
    temp_rect = block_rect.move(j * block_width, i * block_height)
    screen_surface.fill(
        BLACK, 
        temp_rect
    )

    i,j = end_pos
    temp_rect = block_rect.move(j * block_width, i * block_height)
    screen_surface.fill(
        BLACK, 
        temp_rect
    )

    pg.display.flip()