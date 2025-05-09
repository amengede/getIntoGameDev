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

# initialize Scene
# sphere: center, radius, color
spheres = [
    0.0, 0.0, -2.0, 0.5, 45/255, 128/255, 60/255,
    1.0, -0.25, -2.5, 0.25, 192/255, 128/255, 60/255,
    0.0, -100.5, -2.0, 100.0, 45/255, 232/255, 192/255]

# camera: pos, forwards, right, up
camera_pos = [0, 0, 0]
camera_forwards = [0, 0, -1]
camera_right = [1, 0, 0]
camera_up = [0, -1, 0]

#raytracing parameters
samples = 8
bounces = 8

def render_line(screen_y):
     
    for screen_x in range(screen_width):
        
        #set up for trace
        color = [0,0,0]
        largest_dimension = max(screen_width/2, screen_height/2)
        for sample in range(samples):
            horizontal_coefficient = (screen_x + random.uniform(0.0, 1.0) - screen_width / 2) / largest_dimension
            vertical_coefficient = (screen_y + random.uniform(0.0, 1.0) - screen_height / 2) / largest_dimension
            ray_position = [
                camera_pos[0], camera_pos[1], camera_pos[2]]
            ray_direction = [
                camera_forwards[0] + horizontal_coefficient * camera_right[0] + vertical_coefficient * camera_up[0],
                camera_forwards[1] + horizontal_coefficient * camera_right[1] + vertical_coefficient * camera_up[1],
                camera_forwards[2] + horizontal_coefficient * camera_right[2] + vertical_coefficient * camera_up[2]]
            new_color = trace(ray_position, ray_direction, spheres, 0)
            color[0] += new_color[0]
            color[1] += new_color[1]
            color[2] += new_color[2]

        r = max(0,min(255,int(color[0] * 255 / samples)))
        g = max(0,min(255,int(color[1] * 255 / samples)))
        b = max(0,min(255,int(color[2] * 255 / samples)))

        screen_pixels[screen_x][screen_y] = screen.map_rgb((r,g,b))

def trace(ray_position, ray_direction, spheres, bounce):

    alpha = min(1.0, max(0.0, ray_direction[1]))

    color = [1 - alpha, 1 - alpha, 1]
    
    if bounce >= bounces:
        return color

    #pos, normal, t, color
    render_state = [0,0,0,0,0,0,0,0,0,0]
    nearest_hit = 1e30
    hit_something = False
    sphere_count = len(spheres) // 7
    for i in range(sphere_count):
        sphere = spheres[7 * i : 7 * i + 7]
        if hit(ray_position, ray_direction, sphere, 0.001, nearest_hit, render_state, i == 2):
            nearest_hit = render_state[6]
            hit_something = True
        
    if hit_something:
        ray_position[:] = render_state[0:3]

        deflection = random_in_unit_sphere()
        normal = [
            render_state[3] + deflection[0],
            render_state[4] + deflection[1],
            render_state[5] + deflection[2]
        ]
        normal_magnitude = (
             normal[0] * normal[0] 
             + normal[1] * normal[1] 
             + normal[2] * normal[2]) ** 0.5
        ray_direction[0] = normal[0] / normal_magnitude
        ray_direction[1] = normal[1] / normal_magnitude
        ray_direction[2] = normal[2] / normal_magnitude

        new_color = trace(ray_position, ray_direction, spheres, bounce + 1)

        color[0] = render_state[7] * new_color[0]
        color[1] = render_state[8] * new_color[1]
        color[2] = render_state[9] * new_color[2]
    return color

def hit(ray_position, ray_direction, sphere, t_min, t_max, render_state, debug):
        
        center = sphere[0:3]
        radius = sphere[3]
        color = sphere[4:7]

        co = [
            ray_position[0] - center[0],
            ray_position[1] - center[1],
            ray_position[2] - center[2]]
        a = ray_direction[0] * ray_direction[0] \
            + ray_direction[1] * ray_direction[1] \
            + ray_direction[2] * ray_direction[2]
        b = 2 * (co[0] * ray_direction[0] 
                 + co[1] * ray_direction[1] 
                 + co[2] * ray_direction[2])
        c = (co[0] * co[0] + co[1] * co[1] + co[2] * co[2]) - radius * radius
        discriminant = b * b - 4 * a * c
        #if debug:
        #    print(discriminant)
        if discriminant < 0:
            return False
        root = (-b - (discriminant) ** 0.5) / (2 * a)
        if (root < t_min) or (root > t_max):
            root = (-b + (discriminant) ** 0.5) / (2 * a)
            if (root < t_min) or (root > t_max):
                return False
        
        #pos, normal, t, color
        pos = [
            ray_position[0] + root * ray_direction[0],
            ray_position[1] + root * ray_direction[1],
            ray_position[2] + root * ray_direction[2]
        ]
        render_state[0:3] = pos[:]

        displacement = [
            pos[0] - center[0],
            pos[1] - center[1],
            pos[2] - center[2]
        ]
        displacement_magnitude = (displacement[0] * displacement[0] 
                                  + displacement[1] * displacement[1] 
                                  + displacement[2] * displacement[2]) ** 0.5
        
        displacement[0] = displacement[0] / displacement_magnitude
        displacement[1] = displacement[1] / displacement_magnitude
        displacement[2] = displacement[2] / displacement_magnitude

        render_state[3:6] = displacement[:]

        render_state[6] = root
        
        render_state[7:10] = color

        return True

def random_in_unit_sphere():

    radius = random.uniform(0.0, 1.0)
    theta = random.uniform(0.0, 2 * math.pi)
    phi = random.uniform(0.0, math.pi)
    
    return [
        radius * math.cos(theta) * math.cos(phi),
        radius * math.sin(theta) * math.cos(phi),
        radius * math.sin(phi)
    ]

# main loop
def main_loop():
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
            
            render_line(screen_y)

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

if __name__ == "__main__":
    main_loop()