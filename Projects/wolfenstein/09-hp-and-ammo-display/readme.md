# Stage 9: HP & Ammo display
Very simple, store the player's state and display it.

## Storing the state

<controller/game.py>:
```
class Game:

    def __init__(self):

        # ...

        # load map
        self.load_map("level.txt")

        # ...

        # make systems
        self.renderer = Renderer(self.screen_width,
            self.screen_height, self.map,
            self.player, self.player_state)
        # ...
    
    # ...

    def make_player(self, words: list[str]) -> np.ndarray:

        self.player_state = np.array((100, 15), dtype = np.uint8)
        
        # ...
```

Nothing too technical here, just define a numpy array holding all the player's status variables. It's a little annoying to pass it down the line to renderer and its states, but that's ok.

## Displaying

<systems/renderer.py>:
```
class GameRenderer:

    def __init__(self, ...):

        # ...

        self.font = pg.font.Font(size = 48)
    
    def update(self, frametime: float):
        """
            Draws a frame
        """

        # ...
        self.draw_gun(frametime)
        pg.draw.rect(self.screen,
                    (0, 16, 128), (0, 450, 800, 600))
        self.draw_text(f"Health: {self.player_state[0]}",
            (50, 450))
        self.draw_text(f"Ammo: {self.player_state[1]}",
            (450, 450))
    
    def draw_text(self, text: str, pos: tuple[int]) -> None:

        text_surface = self.font.render(text, True, (255,255,255))
        self.screen.blit(text_surface, pos)
```

The health and ammo can be displayed simply enough with a helper function. We may revisit this, but for now it gets the job done!