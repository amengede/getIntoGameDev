from config import *
import model
import view

pg.init()
screen_surface = pg.display.set_mode(SCREEN_SIZE)
running = True

world = model.World()
renderer = view.Renderer(screen_surface)

last_time = pg.time.get_ticks()
current_time = pg.time.get_ticks()
num_frames = 0
frame_time = 0

velocity_x = 0.0
velocity_y = 0.0

while running:

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    
    keys = pg.key.get_pressed()
    if keys[pg.K_LEFT]:
        velocity_x = -20
    if keys[pg.K_RIGHT]:
        velocity_x = 20
    if keys[pg.K_UP]:
        velocity_y = 20
    if keys[pg.K_DOWN]:
        velocity_y = -20
    if keys[pg.K_SPACE]:
        velocity_x = 0.0
        velocity_y = 0.0
    world.update(frame_time, velocity_x, velocity_y)
    #break

    renderer.draw(world.get_bg(), world.get_strands())
    
    current_time = pg.time.get_ticks()
    delta = current_time - last_time
    if (delta >= 1000):
        framerate = int(1000 * num_frames/delta)
        pg.display.set_caption(f"Running at {framerate} fps.")
        last_time = current_time
        num_frames = -1
        frame_time = float(1000.0 / max(1,framerate))
    num_frames += 1