import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *

def draw_wireframe(vertices: tuple[tuple[float]], 
                   indices: tuple[int], 
                   theta: float) -> None:
    glPushMatrix()
    glRotatef(theta, 3, 1, 1)
    glBegin(GL_LINES)
    for index in indices:
        glVertex3fv(vertices[index])
    glEnd()
    glPopMatrix()

vertices= (
    ( 1, -1, -1),
    ( 1,  1, -1),
    (-1,  1, -1),
    (-1, -1, -1),
    ( 1, -1,  1),
    ( 1,  1,  1),
    (-1, -1,  1),
    (-1,  1,  1))

wireframe_indices = (0, 1, 0, 3, 0, 4, 2, 1, 2, 3, 2, 7, 6, 3, 6, 4, 6, 7, 5, 1, 5, 4, 5, 7)

pg.init()
pg.display.set_mode((640, 480), pg.DOUBLEBUF | pg.OPENGL)
clock = pg.time.Clock()

gluPerspective(45, 640 / 480, 0.1, 50.0)

glMatrixMode(GL_MODELVIEW)
glTranslatef(0.0,0.0, -5)

theta = 0.0

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    theta += 1
    if theta > 360:
        theta -= 360

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    draw_wireframe(vertices, wireframe_indices, theta)
    pg.display.flip()
    clock.tick(60)

pg.quit()