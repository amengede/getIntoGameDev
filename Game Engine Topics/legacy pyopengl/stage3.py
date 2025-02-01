import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *

def handle_keys(camera_position: list[float]) -> None:
    keys = pg.key.get_pressed()
    speed = 0.1
    if keys[pg.K_a]:
        camera_position[0] -= speed
    if keys[pg.K_d]:
        camera_position[0] += speed
    if keys[pg.K_w]:
        camera_position[2] -= speed
    if keys[pg.K_s]:
        camera_position[2] += speed

def apply_camera_view(camera_position: list[float]) -> None:

    cam_x, cam_y, cam_z = camera_position
    glPushMatrix()
    glTranslatef(-cam_x, -cam_y, -cam_z)

def apply_rotation(theta) -> None:

    glPushMatrix()
    glRotatef(theta, 3, 1, 1)

def reset_transform() -> None:

    glPopMatrix()

def draw_wireframe(vertices: tuple[tuple[float]], 
                   indices: tuple[int]) -> None:

    glColor3fv((1,1,1))
    glBegin(GL_LINES)
    for index in indices:
        glVertex3fv(vertices[index])
    glEnd()

def draw_filled(vertices: tuple[tuple[float]], 
                colors: tuple[tuple[float]], 
                indices: tuple[int]) -> None:
    
    for edge_table in indices:
        glBegin(GL_TRIANGLE_FAN)
        for index in edge_table:
            glColor3fv(colors[index])
            glVertex3fv(vertices[index])
        glEnd()

vertices= (
    ( 1, -1, -1),
    ( 1,  1, -1),
    (-1,  1, -1),
    (-1, -1, -1),
    ( 1, -1,  1),
    ( 1,  1,  1),
    (-1, -1,  1),
    (-1,  1,  1))

colors = (
    (0,0,0),
    (0,0,1),
    (0,1,0),
    (0,1,1),
    (1,0,0),
    (1,0,1),
    (1,1,0),
    (1,1,1))

wireframe_indices = (0, 1, 0, 3, 0, 4, 2, 1, 2, 3, 2, 7, 6, 3, 6, 4, 6, 7, 5, 1, 5, 4, 5, 7)
face_indices = (
    (0, 1, 2, 3), (3, 2, 7, 6), 
    (6, 7, 5, 4), (4, 5, 1, 0), 
    (1, 5, 7, 2), (4, 0, 3, 6))

pg.init()
pg.display.set_mode((640, 480), pg.DOUBLEBUF | pg.OPENGL)
clock = pg.time.Clock()

gluPerspective(45, 640 / 480, 0.1, 50.0)

glMatrixMode(GL_MODELVIEW)
glEnable(GL_DEPTH_TEST)

theta = 0
camera_position = [0.0, 0.0, 5.0]

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    theta += 1
    if theta > 360:
        theta -= 360

    handle_keys(camera_position)
    
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    apply_camera_view(camera_position)
    apply_rotation(theta)
    draw_filled(vertices, colors, face_indices)
    draw_wireframe(vertices, wireframe_indices)
    reset_transform()
    reset_transform()

    pg.display.flip()
    clock.tick(60)

pg.quit()