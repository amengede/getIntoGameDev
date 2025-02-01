# Stage 3: Loading and Displaying the map
In this stage we're going to load a map from an external file. We'll then draw a top down view of the map, and learn about state machines.

## Map Format
Here's the contents of the map file:

<level.txt>:
```
size 27 18
map
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 2 2 2 0 0 
0 0 3 3 3 3 3 3 3 3 0 0 0 0 0 0 0 0 0 0 2 0 0 0 0 2 0 
0 0 3 0 0 0 0 0 0 3 0 0 0 0 0 0 0 0 0 2 0 0 0 0 0 0 2 
0 0 3 0 0 0 0 0 0 3 0 0 0 0 0 0 0 0 2 0 0 0 0 0 0 0 2 
0 0 3 0 0 6 6 0 0 3 2 2 2 2 2 2 2 2 0 0 0 0 0 0 0 0 2 
0 0 3 0 0 6 6 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 
0 0 3 0 0 0 0 0 0 3 2 0 2 2 2 2 2 2 0 0 0 0 0 0 0 0 2 
0 0 3 0 0 0 0 0 3 0 2 0 2 0 0 0 0 0 2 0 0 0 0 0 0 0 2 
0 0 3 0 0 0 0 0 3 0 2 0 2 0 0 0 0 0 0 2 0 0 0 0 0 0 2 
0 0 3 3 3 3 3 3 3 0 1 0 1 0 0 0 0 0 0 0 2 0 0 0 0 2 0 
0 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 2 2 2 2 0 0 
0 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
end
```
We can load the file and display its contents:

<controller/game.py>:
```
def __init__(self):

    # screen size ...

    # load map
    self.map = self.load_map("level.txt")

    # make systems ...

def load_map(self, filename: str) -> np.ndarray:

    with open(filename, "r") as file:
        line = file.readline()
        while line:
            print(line)
            line = file.readline()
```
Now let's deal with those lines.

### size

The size line specifies the (x,y) size of the map. When we see it, let's allocate a numpy array for the map.

```
    while line:
        line = line.strip()
        words: list[str] = line.split(" ")

        if words[0] == "size":
            game_map = self.allocate_map(words)
        
        line = file.readline()
    
def allocate_map(self, words: list[str]) -> np.ndarray:
    
    w = int(words[1])
    h = int(words[2])
    return np.zeros((w,h), dtype = np.uint8)
```
We've chosen to store each entry as an 8 bit unsigned integer. In general the less memory we use for elements, the faster memory access will be.

### map
The map line indicates the beginning of the map section. When we see it, we'll jump into a map loading function.
```
            #...
            if words[0] == "map":
                self.fill_map(file, game_map)
            
            line = file.readline()
    
    def fill_map(self, file, game_map: np.ndarray) -> np.ndarray:
        
        line = file.readline()
        y = 0

        while line:
            line = line.strip()
            words: list[str] = line.split(" ")

            if words[0] == "end":
                return
            
            x = 0
            for word in words:
                game_map[x][y] = int(word)
                x += 1
            y += 1

            line = file.readline()
```
We essentially read the map one horizontal line at a time. The end tag signals the end of the map section. Here's the full map loading code for completeness:
```
def load_map(self, filename: str) -> np.ndarray:

    with open(filename, "r") as file:
        line = file.readline()

        while line:
            line = line.strip()
            words: list[str] = line.split(" ")

            if words[0] == "size":
                game_map = self.allocate_map(words)
            
            if words[0] == "map":
                self.fill_map(file, game_map)
            line = file.readline()
    
    return game_map
    
def allocate_map(self, words: list[str]) -> np.ndarray:
    
    w = int(words[1])
    h = int(words[2])
    return np.zeros((w,h), dtype = np.uint8)
    
def fill_map(self, file, game_map: np.ndarray) -> np.ndarray:
    
    line = file.readline()
    y = 0

    while line:
        line = line.strip()
        words: list[str] = line.split(" ")

        if words[0] == "end":
            return
        
        x = 0
        for word in words:
            game_map[x][y] = int(word)
            x += 1
        y += 1

        line = file.readline()
```

## Rendering the map
The renderer system can now take the map data in its constructor. This is completely ok because numpy arrays are lightweight data references.

<systmes/renderer.py>:
```
def __init__(self, width: int, height: int, game_map: np.ndarray):

    # ...
        
    self.map_width = len(game_map)
    self.map_height = len(game_map[0])
    print(f"Map measurements: {self.map_width} x {self.map_height}")
    self.map = game_map
```

Of course the game class will need to pass the map data along.

<controller/game.py>
```
def __init__(self):

    # ...

    # make systems
    self.renderer = Renderer(self.screen_width, self.screen_height, self.map)
    self.clock = pg.time.Clock()
```

Now in the initializer we can calculate the width and height of each grid square, to stretch the map to the size of the screen.
<systmes/renderer.py>:
```
def __init__(self, width: int, height: int, game_map: np.ndarray):

    # ...
        
    self.map_width = len(game_map)
    self.map_height = len(game_map[0])
    self.map = game_map
    self.grid_size = (
        int(self.width / self.map_width), 
        int(self.height / self.map_height))
```
While we're at it, it'll be much easier to draw the grid if the draw_rectangle function takes in a top-left corner and size.

```
@njit()
def draw_rectangle(color_buffer: np.ndarray, color: int,
                   top_left: tuple[int], size: tuple[int]) -> None:
    
    x1, y1 = top_left
    w, h = size
    
    for x in range(x1, x1 + w):
        color_buffer[x][y1:y1 + h] = color
```

The rendering code then becomes a lot simpler. Let's split the top down and perspective views into two individual methods.
```
def update(self):

    if self.map_mode:
        self.draw_map()
    else:
        self.draw_world()
        
    pg.surfarray.blit_array(self.screen_surface, self.screen_pixels)
    pg.display.flip()
    
def draw_world(self):

    #ceiling
    top_left = (0, 0)
    size = (self.width, int(self.height / 2))
    draw_rectangle(self.screen_pixels, self.colors[2], top_left, size)

    #floor
    top_left = (0, int(self.height / 2))
    draw_rectangle(self.screen_pixels, self.colors[3], top_left, size)

def draw_map(self):

    clear_screen(self.screen_pixels, self.colors[0])

    for x in range(0, self.width, 40):
        draw_vertical_line(self.screen_pixels, self.colors[1], x, 0, self.height)
    
    for y in range(0, self.height, 40):
        draw_horizontal_line(self.screen_pixels, self.colors[1], 0, self.width, y)
```

Now onto the map! First of all let's get the grid properly sized.
```
def draw_map(self):

    clear_screen(self.screen_pixels, self.colors[0])

    for x in range(0, self.width, self.grid_size[0]):
        draw_vertical_line(self.screen_pixels, self.colors[1], x, 0, self.height)
    
    for y in range(0, self.height, self.grid_size[1]):
        draw_horizontal_line(self.screen_pixels, self.colors[1], 0, self.width, y)
```

We can then define some new colors in the renderer's palette for the walls.
```
self.colors = (
    self.screen_surface.map_rgb(  0,   0,   0), #black
    self.screen_surface.map_rgb(255, 255, 255), #white
    self.screen_surface.map_rgb( 56,  56,  56), #ceiling
    self.screen_surface.map_rgb(112, 112, 112), #floor
    self.screen_surface.map_rgb(  0,   0, 255), #color 1
    self.screen_surface.map_rgb(255, 255,   0), #color 2
    self.screen_surface.map_rgb(  0, 255, 255), #color 3
    self.screen_surface.map_rgb(  0, 255,   0), #color 4
    self.screen_surface.map_rgb(255,   0, 255), #color 5
    self.screen_surface.map_rgb(255,   0,   0), #color 6
    )
```

And finally we can draw the map! The idea is to loop through the map, draw any walls, and then to finally draw the grid over the top.
```
def draw_map(self):

    clear_screen(self.screen_pixels, self.colors[0])

    for x in range(self.map_width):
        for y in range(self.map_height):
            tile = self.map[x][y]
            if tile == 0:
                continue

            color = self.colors[tile + 3]
            top_left = (x * self.grid_size[0], y * self.grid_size[1])
            draw_rectangle(self.screen_pixels, color, top_left, self.grid_size)

    for x in range(0, self.width, self.grid_size[0]):
        draw_vertical_line(self.screen_pixels, self.colors[1], x, 0, self.height)
    
    for y in range(0, self.height, self.grid_size[1]):
        draw_horizontal_line(self.screen_pixels, self.colors[1], 0, self.width, y)
```

## State Machines
Our renderer currently has two modes, we could control this with a simple toggle.

<systems/renderer.py>
```
def toggle_draw_mode(self):

    self.map_mode = not self.map_mode
```

<controller/game.py>:
```
def play(self):

    running = True
    while (running):
        #events
        for event in pg.event.get():

            if (event.type == pg.KEYDOWN and event.key == pg.K_TAB):
                self.renderer.toggle_draw_mode()
            # ...
```

This is fine, but it won't scale well, and it gives us an opportunity to examine a more elegant approach, state machines. Let's define a class for each draw mode.

<systems/renderer.py>:
```
class Renderer:
    
    # ...

class GameRenderer:

    def __init__(self, width: int, height: int, 
                 game_map: np.ndarray, colors: tuple[int], 
                 screen_pixels: np.ndarray):

        self.width = width
        self.height = height
        self.screen_pixels = screen_pixels
        self.colors = colors
    
    def update(self):
        """
            Draws a frame
        """

        #ceiling
        top_left = (0, 0)
        size = (self.width, int(self.height / 2))
        draw_rectangle(self.screen_pixels, self.colors[2], top_left, size)

        #floor
        top_left = (0, int(self.height / 2))
        draw_rectangle(self.screen_pixels, self.colors[3], top_left, size)

class MapRenderer:

    def __init__(self, width: int, height: int, 
                 game_map: np.ndarray, colors: tuple[int], 
                 screen_pixels: np.ndarray):

        self.width = width
        self.height = height
        self.screen_pixels = screen_pixels
        self.colors = colors
        
        self.map_width = len(game_map)
        self.map_height = len(game_map[0])
        self.map = game_map
        self.grid_size = (
            int(self.width / self.map_width), 
            int(self.height / self.map_height))
        
    def update(self):
        """
            Draws a frame
        """

        clear_screen(self.screen_pixels, self.colors[0])

        for x in range(self.map_width):
            for y in range(self.map_height):
                tile = self.map[x][y]
                if tile == 0:
                    continue

                color = self.colors[tile + 3]
                top_left = (x * self.grid_size[0], y * self.grid_size[1])
                draw_rectangle(self.screen_pixels, color, top_left, self.grid_size)

        for x in range(0, self.width, self.grid_size[0]):
            draw_vertical_line(self.screen_pixels, self.colors[1], x, 0, self.height)
        
        for y in range(0, self.height, self.grid_size[1]):
            draw_horizontal_line(self.screen_pixels, self.colors[1], 0, self.width, y)
```

With the drawing behaviour and state offloaded to helper classes, the Renderer itself can now be made simpler. There are more elaborate abstractions we can use here, but they're not really worth it right now.
```
class Renderer:
    """
        Responsible for drawing scenes
    """

    def __init__(self, width: int, height: int, game_map: np.ndarray):
        """
            Initialize a rendering engine.
            
                Parameters:
                    width (int): width of screen
                    height (int): height of screen
        """

        pg.init()
        self.screen_surface = pg.display.set_mode((width, height))
        self.screen_pixels = pg.surfarray.array2d(self.screen_surface)

        colors = (
            self.screen_surface.map_rgb(  0,   0,   0), #black
            self.screen_surface.map_rgb(255, 255, 255), #white
            self.screen_surface.map_rgb( 56,  56,  56), #ceiling
            self.screen_surface.map_rgb(112, 112, 112), #floor
            self.screen_surface.map_rgb(  0,   0, 255), #color 1
            self.screen_surface.map_rgb(255, 255,   0), #color 2
            self.screen_surface.map_rgb(  0, 255, 255), #color 3
            self.screen_surface.map_rgb(  0, 255,   0), #color 4
            self.screen_surface.map_rgb(255,   0, 255), #color 5
            self.screen_surface.map_rgb(255,   0,   0), #color 6
            )

        self.states = (
            GameRenderer(width, height, game_map, colors, self.screen_pixels),
            MapRenderer(width, height, game_map, colors, self.screen_pixels)
        )
        self.state_index = 0
        self.state = self.states[self.state_index]
    
    def toggle_draw_mode(self):

        # toggles: 0 -> 1, 1 -> 0
        self.state_index = (self.state_index + 1) % 2
        self.state = self.states[self.state_index]
    
    def update(self):
        """
            Draws a frame
        """

        self.state.update()
            
        pg.surfarray.blit_array(self.screen_surface, self.screen_pixels)
        pg.display.flip()
```
And there we have it! We should now have a handy map view which we can toggle with the tab key. In the next video we're going to add a player object and start moving them around. It may surprise you that we're not really touching 3D yet, but the truth is debugging 3D applications is hard, and we'll have a much better time if the core game features are solid first.