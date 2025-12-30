from config import *
from gameObjects import *
from assets import *

layout =   [[1,1,1,1,1,1,1,1,1,1],
            [1,0,1,0,1,0,1,0,0,1],
            [1,0,1,0,0,0,1,0,1,1],
            [1,0,0,0,1,1,1,2,0,1],
            [1,0,1,0,0,0,0,0,1,1],
            [1,0,1,0,1,1,1,0,1,1],
            [1,0,1,0,1,0,0,0,1,1],
            [1,0,1,0,1,1,1,0,1,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1]]

board = GameBoard(layout)
keys = {pg.K_UP:1,pg.K_DOWN:2,pg.K_LEFT:4,pg.K_RIGHT:8}
currentKey = 0
running = True
while running:
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running = False
        if event.type==pg.KEYDOWN:
            if event.key in keys:
                currentKey += keys[event.key]
        if event.type==pg.KEYUP:
            if event.key in keys:
                currentKey -= keys[event.key]
    board.handleKeys(currentKey)
    board.update()
    glClearDepth(1000.0)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    board.draw()
    pg.display.flip()
    clock.tick()
    fps = clock.get_fps()
    pg.display.set_caption("Running at "+str(int(fps))+" fps")

pg.quit()