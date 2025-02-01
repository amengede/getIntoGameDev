# Stage 2: Horizontal Lines
In this stage we're going to draw horizontal and vertical lines. This will allow us to render the floor and ceiling. We'll also look at using numba to optimize our code.

## Old dog, new tricks
Let's make some additions to the renderer's initializer. First we'll store the size of the window.

<systems/renderer.py>:
```
def __init__(self, width: int, height: int):

    pg.init()
    self.width = width
    self.height = height
    #...
```

And update the color palette.
```
self.colors = (
    self.screen_surface.map_rgb(0, 0, 0),       #black
    self.screen_surface.map_rgb(255, 255, 255), #white
    self.screen_surface.map_rgb(56, 56, 56),    #ceiling
    self.screen_surface.map_rgb(112, 112, 112), #floor
    )
```

## Vertical Lines

To draw a vertical line, we simply take in a number representing the color we want to draw, and copy it to a slice of the color buffer. Let's define a function to do this.
```
def draw_vertical_line(color_buffer: np.ndarray, color: int, 
                  x: int, y1: int, y2: int) -> None:

    color_buffer[x][y1:y2] = color
```

We can test this by drawing some vertical lines in the renderer's update method.
```
def update(self):

    for x in range(0, self.width, 40):
        draw_vertical_line(self.screen_pixels, self.colors[1], x, 0, self.height)
    
    #...
```

## Horizontal Lines
That was pretty straightforward! Let's try the same for horizontal lines.

```
def draw_horizontal_line(color_buffer: np.ndarray, color: int, 
                  x1: int, x2: int, y: int) -> None:

    color_buffer[x1:x2][y] = color
```

Now let's write some code to test it.
```
def update(self):

    # vertical lines ...

    for y in range(0, self.height, 40):
        draw_horizontal_line(self.screen_pixels, self.colors[1], 0, self.width, y)
    
    #...
```
It doesn't work! Our color buffer is an array of arrays, so the x coordinate is used to select a vertical line of the screen, and then the y coordinate is used to access into that vertical line. The upshot of this is that we can't write to a range of x coordinates at the same time.

We can still draw horizontal lines, but a for loop is needed.
```
def draw_horizontal_line(color_buffer: np.ndarray, color: int, 
                  x1: int, x2: int, y: int) -> None:

    for x in range(x1, x2):
        color_buffer[x][y] = color
```

## Rectangles
Now let's write a function to fill a rectangular region of the screen. We'll achieve this by repeatedly drawing lines to fill the whole space. As we saw before, vertical lines are simpler than horizontal lines, so let's fill the rectangle with vertical lines.
```
def draw_rectangle(color_buffer: np.ndarray, color: int,
                   x1: int, y1: int, x2: int, y2: int) -> None:
    
    for x in range(x1, x2):
        draw_vertical_line(color_buffer, color, x, y1, y2)
```

It's probably worth mentioning Pygame's coordinate system. In Pygame, coordinates run from left to right and top to bottom, so the left of our screen is x = 0, the right of our screen is x = 639, the top of our screen is y = 0 and the bottom of our screen is y = 479.

With that in mind, let's draw the ceiling and floor. Now that we're filling the whole screen, the clear screen method isn't needed.
```
def update(self):

    #ceiling
    draw_rectangle(self.screen_pixels, self.colors[2], 0, 0, self.width, self.height // 2)

    #floor
    draw_rectangle(self.screen_pixels, self.colors[3], 0, self.height // 2, self.width, self.height)

    #...
```

## Numba
Given that we're running a for loop in python, performance is surprisingly good on my machine, but we can make things faster.

Numba is a python package which offers just in time compilation. Usually in python, function calls are all handled inside the interpreter. With numba we can mark a function for compilation. Numba then intercepts the function call, inspects the data types of the arguments and then dispatches the function call to a machine code compiled version. The first function call is slow as compilation occurs, but when it's warmed up the speedups can be incredible. Numba also is designed to work well with numpy arrays.

Let's mark our rectangle function for compilation. Because it calls the vertical_line function, that function will also need to be marked. This is because the compiled machine code has no idea how to call python code.
```
@njit()
def draw_vertical_line(color_buffer: np.ndarray, color: int, 
                  x: int, y1: int, y2: int) -> None:

    color_buffer[x][y1:y2] = color

@njit()
def draw_rectangle(color_buffer: np.ndarray, color: int,
                   x1: int, y1: int, x2: int, y2: int) -> None:
    
    for x in range(x1, x2):
        color_buffer[x][y1:y2] = color
```

But we can do better. Numba will skip the dispatch selection if we tell it upfront what data types we're expecting parameters to have. This is called eager compilation. Let's head to the config file and import the 32 bit integer type.

<config.py>
```
#...
from numba import int32
```

We can then decorate the functions.
```
@njit((int32[:,:], int32, int32, int32, int32))
def draw_vertical_line(color_buffer: np.ndarray, color: int, 
                  x: int, y1: int, y2: int) -> None:

    color_buffer[x][y1:y2] = color

@njit((int32[:,:], int32, int32, int32, int32, int32))
def draw_rectangle(color_buffer: np.ndarray, color: int,
                   x1: int, y1: int, x2: int, y2: int) -> None:
    
    for x in range(x1, x2):
        color_buffer[x][y1:y2] = color
```

## Inlining
Function calls aren't free. In the process of calling a function, all local variables are saved and restored.
```
def function1():

    #...
    # save f1 state (happens in background)
    function2()
    # restore f1 state (happens in background)


def function2():
    
    #...
```
A common optimization is function inlining, preferring some code repetition over context switching. We can take the vertical line code and paste it into the draw_rectangle function. This has the added benefit that draw_vertical_line doesn't need to be compiled, for now.
```
def draw_vertical_line(color_buffer: np.ndarray, color: int, 
                  x: int, y1: int, y2: int) -> None:

    color_buffer[x][y1:y2] = color

@njit((int32[:,:], int32, int32, int32, int32, int32))
def draw_rectangle(color_buffer: np.ndarray, color: int,
                   x1: int, y1: int, x2: int, y2: int) -> None:
    
    for x in range(x1, x2):
        color_buffer[x][y1:y2] = color
```

And that's it! In the next stage we'll load in a map from a text file.