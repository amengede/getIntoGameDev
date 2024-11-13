import pygame as pg
import random
import math
import time

# Initialize Pygame
pg.init()
screen_width = 640
screen_height = 480
screen = pg.display.set_mode((screen_width, screen_height))
screen_pixels = pg.surfarray.array2d(screen)
clock = pg.time.Clock()

#---- Scratch Memory ----#
cache_size = 32
cache = [0.0 for _ in range(cache_size)]
#------------------------#

# initialize Scene
# sphere: center, radius, color
spheres = [
    0.0, 0.0, -2.0, 0.5, 45/255, 128/255, 60/255,
    1.0, -0.25, -2.5, 0.25, 192/255, 128/255, 60/255,
    0.0, -100.5, -2.0, 100.0, 45/255, 232/255, 192/255]
sphere_count = len(spheres)

# camera: pos, forwards, right, up
camera_pos = [0.0, 0.0, 0.0]
cache[0] = camera_pos[0]
cache[1] = camera_pos[1]
cache[2] = camera_pos[2]
camera_forwards = [0.0, 0.0, -1.0]
cache[3] = camera_forwards[0]
cache[4] = camera_forwards[1]
cache[5] = camera_forwards[2]
camera_right = [1.0, 0.0, 0.0]
cache[6]  = camera_right[0]
cache[7]  = camera_right[1]
cache[8]  = camera_right[2]
camera_up = [0.0, -1.0, 0.0]
cache[9]  = camera_up[0]
cache[10] = camera_up[1]
cache[11] = camera_up[2]

#raytracing parameters
samples = 8
bounces = 8

def render_line(screen_y, cache):

    largest_dimension = max(screen_width/2, screen_height/2)
    vertical_coefficient = (screen_y - screen_height / 2) / largest_dimension
    horizontal_coefficient = -1.0
    dx = 1.0 / largest_dimension

    for screen_x in range(screen_width):
        horizontal_coefficient += dx  
        color = [0.0, 0.0, 0.0]
        for _ in range(samples):
            cache[12] = cache[0]
            cache[13] = cache[1]
            cache[14] = cache[2]
            temp_x = horizontal_coefficient + random.random() * dx
            temp_y = vertical_coefficient + random.random() * dx
            cache[15] = cache[3] + temp_x * cache[6] + temp_y * cache[9]
            cache[16] = cache[4] + temp_x * cache[7] + temp_y * cache[10]
            cache[17] = cache[5] + temp_x * cache[8] + temp_y * cache[11]
            new_color = trace(cache, spheres, 0)
            color[0] = color[0] + new_color[0]
            color[1] = color[1] + new_color[1]
            color[2] = color[2] + new_color[2]
        
        r = min(255,int(color[0] * 255 / samples))
        g = min(255,int(color[1] * 255 / samples))
        b = min(255,int(color[2] * 255 / samples))

        screen_pixels[screen_x][screen_y] = screen.map_rgb((r,g,b))

def trace(cache, spheres, bounce):

    color = [1 - cache[16], 1 - cache[16], 1]
    
    if bounce >= bounces:
        return color

    cache[22] = 1e30
    hit_something = False
    for i in range(0, sphere_count, 7):
        cache[18] = spheres[i]
        cache[19] = spheres[i + 1]
        cache[20] = spheres[i + 2]
        cache[21] = spheres[i + 3]
        if hit(cache):
            hit_something = True
            color[0] = spheres[i + 4]
            color[1] = spheres[i + 5]
            color[2] = spheres[i + 6]
        
    if hit_something:
        cache[12] = cache[23]
        cache[13] = cache[24]
        cache[14] = cache[25]

        random_in_unit_sphere(cache)
        
        normal_magnitude = (
            cache[26] * cache[26] 
            + cache[27] * cache[27] 
            + cache[28] * cache[28]) ** 0.5
        cache[15] = cache[26] / normal_magnitude
        cache[16] = cache[27] / normal_magnitude
        cache[17] = cache[28] / normal_magnitude

        new_color = trace(cache, spheres, bounce + 1)

        color[0] = color[0] * new_color[0]
        color[1] = color[1] * new_color[1]
        color[2] = color[2] * new_color[2]
    return color

def hit(cache):

    co = [
        cache[12] - cache[18],
        cache[13] - cache[19],
        cache[14] - cache[20]]
    a = cache[15] * cache[15] \
        + cache[16] * cache[16] \
        + cache[17] * cache[17]
    b = 2 * (co[0] * cache[15] 
                + co[1] * cache[16] 
                + co[2] * cache[17])
    c = (co[0] * co[0] + co[1] * co[1] + co[2] * co[2]) - cache[21] * cache[21]
    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return False
    root = (-b - (discriminant) ** 0.5) / (2 * a)
    if (root < 0.001) or (root > cache[22]):
        return False
    
    cache[22] = root
    
    #pos, normal, t, color
    cache[23] = cache[12] + root * cache[15]
    cache[24] = cache[13] + root * cache[16]
    cache[25] = cache[14] + root * cache[17]

    cache[26] = cache[23] - cache[18]
    cache[27] = cache[24] - cache[19]
    cache[28] = cache[25] - cache[20]

    # magnitude
    magnitude = (cache[26] * cache[26]
                + cache[27] * cache[27]
                + cache[28] * cache[28]) ** 0.5
    
    cache[26] = cache[26] / magnitude
    cache[27] = cache[27] / magnitude
    cache[28] = cache[28] / magnitude

    return True

def random_in_unit_sphere(cache):

    # radius, theta, phi
    radius = random.random()
    theta = random.random() * 2 * math.pi
    phi = random.random() * math.pi
    cos_theta = math.cos(phi)
    
    cache[26] = cache[26] + radius * math.cos(theta) * cos_theta
    cache[27] = cache[27] + radius * math.sin(theta) * cos_theta
    cache[28] = cache[28] + radius * math.sin(phi)

# main loop
running = True
screen_y = 0
i = 0
rendered = False
start = time.time()
while (running):
            
    #events
    for event in pg.event.get():
        if (event.type == pg.QUIT):
                    running = False
            
    #render
    if (not rendered):
        render_line(screen_y, cache)

        screen_y = (screen_y + 1) % screen_height

        if screen_y == 0:
            rendered = True
            finish = time.time()
            print(f"Render took {finish - start} seconds")
    
    pg.surfarray.blit_array(screen, screen_pixels)
    pg.display.flip()

    #timing
    clock.tick()
    framerate = int(clock.get_fps())
    pg.display.set_caption(f"Running at {framerate} fps.")

pg.quit()