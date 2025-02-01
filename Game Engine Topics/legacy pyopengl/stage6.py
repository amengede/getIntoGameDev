import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
import math

def handle_keys(camera_position: list[float], camera_eulers: list[float]) -> None:

    theta_forwards = math.radians(camera_eulers[0])
    cos_theta_forwards = math.cos(theta_forwards)
    sin_theta_forwards = math.sin(theta_forwards)

    theta_right = math.radians(camera_eulers[0] + 90)
    cos_theta_right = math.cos(theta_right)
    sin_theta_right = math.sin(theta_right)

    keys = pg.key.get_pressed()
    speed = 0.1
    if keys[pg.K_a]:
        camera_position[0] -= speed * sin_theta_right
        camera_position[2] -= speed * cos_theta_right
    if keys[pg.K_d]:
        camera_position[0] += speed * sin_theta_right
        camera_position[2] += speed * cos_theta_right
    if keys[pg.K_w]:
        camera_position[0] -= speed * sin_theta_forwards
        camera_position[2] -= speed * cos_theta_forwards
    if keys[pg.K_s]:
        camera_position[0] += speed * sin_theta_forwards
        camera_position[2] += speed * cos_theta_forwards

def handle_mouse(camera_eulers: list[float]) -> None:
    current_pos = pg.mouse.get_pos()
    speed = 0.1

    dx = current_pos[0] - 320
    dy = 240 - current_pos[1]
    if abs(dx) + abs(dy) > 0:

        #theta
        camera_eulers[0] -= speed * dx
        if camera_eulers[0] > 360:
            camera_eulers[0] -= 360
        if camera_eulers[0] < 0:
            camera_eulers[0] += 360
        
        #phi
        camera_eulers[1] = min(89, max(-89, camera_eulers[1] + speed * dy))

        pg.mouse.set_pos(320, 240)

def apply_camera_view(camera_position: list[float], 
                      camera_eulers: list[float]) -> None:

    cam_x, cam_y, cam_z = camera_position
    theta, phi = camera_eulers
    glPushMatrix()
    glRotatef(-phi, 1, 0, 0)
    glRotatef(-theta, 0, 1, 0)
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
pg.mouse.set_visible(False)
clock = pg.time.Clock()

gluPerspective(45, 640 / 480, 0.1, 50.0)

glMatrixMode(GL_MODELVIEW)
glEnable(GL_DEPTH_TEST)

theta = 0
camera_position = [0.0, 0.0, 5.0]
camera_eulers = [0.0, 0.0]

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            running = False

    theta += 1
    if theta > 360:
        theta -= 360

    handle_keys(camera_position, camera_eulers)
    handle_mouse(camera_eulers)
    
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    apply_camera_view(camera_position, camera_eulers)
    apply_rotation(theta)
    draw_filled(vertices, colors, face_indices)
    draw_wireframe(vertices, wireframe_indices)
    reset_transform()
    reset_transform()

    pg.display.flip()
    clock.tick(60)

pg.quit()