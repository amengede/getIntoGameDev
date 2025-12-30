import pygame as pg
import numpy as np
import heapq

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
GREY = (64, 64, 64)

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

def reset_search():

    to_expand = []
    heapq.heappush(to_expand, (0, start_pos))
    history = []
    predecessor = {}

    return (to_expand, history, predecessor)

def get_neighbours(pos: tuple[int]) -> list[tuple[int]]:

    i,j = pos

    i_above = max(0, i - 1)
    i_below = min(len(blocks) - 1, i + 1)
    j_right = min(len(blocks[0]) - 1, j + 1)
    j_left = max(0, j - 1)

    return [
        (i, j_left), (i, j_right),
        (i_above, j), (i_below, j)
    ]

def progress_search(
    to_expand: list[tuple[int]], 
    history: list[tuple[int]],
    predecessor: dict[tuple[int],tuple[int]]):

    #is the search done?
    if len(to_expand) == 0 or end_pos in predecessor:
        print(f"Search finished, {len(history)} checks performed")
        return

    #get the next point to search
    cost, pos = heapq.heappop(to_expand)
    while pos in history:
        cost, pos = heapq.heappop(to_expand)
    history.append(pos)

    points = get_neighbours(pos)
    for new_pos in points:

        #ignore invalid points
        if new_pos in history or new_pos in to_expand:
            continue
        
        if new_pos not in predecessor:
            predecessor[new_pos] = pos
        
        new_cost = blocks[new_pos[0]][new_pos[1]]
        heapq.heappush(to_expand, (cost + new_cost, new_pos))

to_expand, history, predescessor = reset_search()
#--------------------------------------#

block_width = SCREEN_SIZE[0] / len(blocks[0])
block_height = SCREEN_SIZE[1] / len(blocks)
block_rect = pg.Rect(0, 0, block_width,  block_height)

running = True
while running:

    for event in pg.event.get():

        if event.type == pg.QUIT:
            running = False
        
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                to_expand, history, predescessor = reset_search()
            elif event.key == pg.K_SPACE:
                progress_search(to_expand, history, predescessor)
    
    screen_surface.fill(BACKGROUND_COLOR)

    for i,row in enumerate(blocks):
        for j,cost in enumerate(row):
            temp_rect = block_rect.move(j * block_width, i * block_height)
            screen_surface.fill(
                COLORS[cost], 
                temp_rect
            )

            if (i,j) in history:
                screen_surface.fill(
                    GREY, 
                    temp_rect,
                    pg.BLEND_ADD
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

    pos = end_pos
    while pos in predescessor:

        i,j = pos
        temp_rect = block_rect.move(j * block_width, i * block_height)
        screen_surface.fill(
            BLACK, 
            temp_rect
        )

        pos = predescessor[pos]

    pg.display.flip()