from config import *
import model
import view

pg.init()
screen_surface = pg.display.set_mode(SCREEN_SIZE)
simulation = False
running = True

world = model.World()
renderer = view.Renderer(screen_surface)

last_time = pg.time.get_ticks()
current_time = pg.time.get_ticks()
num_frames = 0
frame_time = 0

while running:

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            simulation = not simulation
    world.update(frame_time, simulation)

    renderer.draw(world.get_boxes(), world.get_particles(), simulation)
    
    current_time = pg.time.get_ticks()
    delta = current_time - last_time
    if (delta >= 1000):
        framerate = int(1000 * num_frames/delta)
        pg.display.set_caption(f"Running at {framerate} fps.")
        last_time = current_time
        num_frames = -1
        frame_time = float(1000.0 / max(1,framerate))
    num_frames += 1