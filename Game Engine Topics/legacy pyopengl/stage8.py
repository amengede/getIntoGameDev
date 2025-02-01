import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np

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

def apply_rotation(theta: float, normals: tuple[np.ndarray]) -> list[np.ndarray]:

    glPushMatrix()
    glRotatef(theta, 0, 1, 0)

    #construct rotation matrix
    c = np.cos(np.radians(theta))
    s = np.sin(np.radians(theta))

    m = np.array(
        ((c, 0, -s),
         (0, 1, 0),
         (s, 0, c)),
         dtype = np.float32)

    new_normals = [m.dot(n) for n in normals]
    return new_normals

def reset_transform() -> None:

    glPopMatrix()

def set_up_opengl() -> None:

    gluPerspective(45, 640 / 480, 0.1, 50.0)

    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)

def load_texture(filename: str) -> int:

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    
    image = pg.image.load(filename).convert_alpha()
    width, height = image.get_rect().size
    data = pg.image.tobytes(image, "RGBA")
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture

def draw_filled(vertices: tuple[tuple[float]], 
                colors: tuple[tuple[float]], 
                tex_coords: tuple[tuple[float]],
                normals: tuple[tuple[float]],
                indices: tuple[int], texture: int) -> None:
    
    glBindTexture(GL_TEXTURE_2D, texture)

    light = ambient_color.copy()
    light_to_plane = light_position - plane_center

    for face_index, edge_table in enumerate(indices):

        light += diffuse_color * max(0.0, np.dot(light_to_plane, normals[face_index]))

        glBegin(GL_TRIANGLE_FAN)
        
        for index in edge_table:
            color = np.multiply(light, colors[index])
            glColor3fv(color)
            glTexCoord2fv(tex_coords[index])
            glVertex3fv(vertices[index])
        glEnd()

vertices= (
    ( 1, -1, 0),
    ( 1,  1, 0),
    (-1,  1, 0),
    (-1, -1, 0))

colors = (
    np.array((0,0,1), dtype=np.float32),
    np.array((0,1,0), dtype=np.float32),
    np.array((0,1,1), dtype=np.float32),
    np.array((1,0,0), dtype=np.float32))

tex_coords = (
    (1,1),
    (1,0),
    (0,0),
    (0,1))

normals = (
    np.array((0, 0, 1), dtype=np.float32),)

indices = (
    (0, 1, 2, 3),)

plane_center = np.array([0, 0, 0], dtype=np.float32)
light_position = np.array([0, 0, 5.0], dtype=np.float32)
ambient_color = np.array([0.5, 0.5, 0.5], dtype=np.float32)
diffuse_color = np.array([0.5, 0.5, 0.5], dtype=np.float32)

pg.init()
pg.display.set_mode((640, 480), pg.DOUBLEBUF | pg.OPENGL)
pg.mouse.set_visible(False)
clock = pg.time.Clock()

set_up_opengl()
texture = load_texture("img/stella.png")

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
    new_normals = apply_rotation(theta, normals)
    draw_filled(vertices, colors, tex_coords, new_normals, indices, texture)
    reset_transform()
    reset_transform()

    pg.display.flip()
    clock.tick(60)

pg.quit()