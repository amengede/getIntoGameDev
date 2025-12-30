# Stage 10: Hurt, Heal and Pickup
Previously we made some player state: health and ammo. Now let's modify that state and make the screen flash!

## Hooking up to keypresses

For now we'll hook events up to keypresses. Later when we actually have game objects it'll be easy enough to use the events we're testing now.

We'll start by defining some event codes.

<config.py>:
```
# ...
MESSAGE_TYPE_PLAYER_HURT = 4
MESSAGE_TYPE_PLAYER_HEAL = 5
MESSAGE_TYPE_PLAYER_PICKUP = 6
```

Then our game can publish those events. For now, bind them to the z, x, c keys.

<controller/game.py>:
```
def play(self):

    # ...
    if (event.key == pg.K_ESCAPE):
        running = False
    # ---- DEBUG ZONE BELOW ---- #
    if (event.key == pg.K_z):
        publish(MESSAGE_TYPE_PLAYER_HURT, self.observers)
        self.player_state[0] = max(0, self.player_state[0] - 5)
    if (event.key == pg.K_x):
        publish(MESSAGE_TYPE_PLAYER_HEAL, self.observers)
        self.player_state[0] = min(100, self.player_state[0] + 10)
    if (event.key == pg.K_c):
        publish(MESSAGE_TYPE_PLAYER_PICKUP, self.observers)
        self.player_state[1] = min(50, self.player_state[1] + 15)
        
    # ...
```

## Screen Flashing

If we play the game now, we should see that the numbers in our HUD are changing appropriately, but this isn't very exciting. Let's make the game more exciting by flashing colors on the screen!

Our Game Renderer is in charge of drawing the world. We'd like to be able to add some modifiers to that view, which are time-based. let's give the game renderer a set of timers associated with each of the events.

<systems/renderer.py>:
```
class GameRenderer:

    def __init__(self, ...):

        # ...

        self.timers = np.zeros(3, dtype=np.float32)
    
```

Every step of the Game Renderer's update, those timers are counting down to zero.
```
def update(self, frametime: float):
    """
        Draws a frame
    """

    for i in range(len(self.timers)):
        self.timers[i] = max(0.0, self.timers[i] - frametime)
    
    # ...
```

When the Game Renderer sees that an event has occurred, it sets the timer for that event.
```
for event in self.event_queue:
    # ...
    elif event == MESSAGE_TYPE_PLAYER_HURT:
        self.timers[0] = 200.0
    elif event == MESSAGE_TYPE_PLAYER_HEAL:
        self.timers[1] = 200.0
    elif event == MESSAGE_TYPE_PLAYER_PICKUP:
        self.timers[2] = 200.0
```

Now we can use the timers to calculate a color to tint the screen with. Let's say hurt events will turn the screen red, heal will turn the screen cyan and pickup will turn the screen yellow. This is just one aproach of many, the basic idea is to divide each timer by 200, so the timer is somewhere between 0 and 1, then use those as coefficients in combining three colors, remembering to clip the maximum intensity.
```
tint_r = min(255, int(255 * 0.005 * (self.timers[0] + self.timers[2])))
tint_g = min(255, int(255 * 0.005 * (self.timers[1] + self.timers[2])))
tint_b = min(255, int(255 * 0.005 * self.timers[1]))
tint_color = self.screen.map_rgb((tint_r, tint_b, tint_g))
```
There are probably more sophisticated ways to do it, but an easy approach is to take a bitwise or of the color with the screen pixels.
```
self.screen_pixels |= tint_color
pg.surfarray.blit_array(self.screen, self.screen_pixels)
```

And there we have it! The screen is flashing!