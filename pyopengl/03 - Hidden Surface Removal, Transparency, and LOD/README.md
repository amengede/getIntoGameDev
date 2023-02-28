# COSC3000 Practical 3:
## Hidden Surface Removal, Transparency, MSAA and LOD
Welcome back! Hopefully last week went ok and you're confident setting up cameras, maybe you even have ideas for a camera you could use in your project. Anyway, the goals of this prac are:\
 - to examine and understand the depth buffer
 - to understand how to set up alpha blending
 - to understand how draw order affects results when transparency is added.
 - as a stretch goal, to look at Multisample Antialiasing and Level of Detail.
### Program design: the Model View Control pattern
Before we get into the work, take a look at the start point of the "depth testing" folder, note how the code has been refactored into Model, View and Control sections. This is the sort of design pattern I prefer in my own projects. The breakdown is:

* model: Game objects (component, camera) and logic/manager (scene)
* view: Renderer and engine assets (just meshes right now, materials will be added later)
* control: High level control of the program, runs the main loop, takes user input and measures framerate

It's also worth noting that the renderer is now storing meshes in a dictionary, and querying them on an individual basis. This is to make the engine more general.

### 1: Depth Testing

Let's run this program and, well, run around a bit and view the scene from a few angles. Does it look alright? Not quite! The triangles are drawn out of order! Let's address that.

By default, OpenGL will literally just draw things in the order that they're called. We do, however, have a framebuffer created for us that we can use. A framebuffer typically has three components:

* Color buffer: 32 bits, stores the RGBA color of each pixel on the screen
* Depth buffer: 24 bits, stores the  depth value of each pixel on the screen, typically the depth and stencil buffer are stored together to make a full 32 bits
* Depth buffer: 8 bits, stores extra info that can be used for custom pixel tests. Stencil buffer effects can get pretty creative, typically the depth and stencil buffer are stored together to make a full 32 bits

So our program is storing depth information for each pixel, we just need to enable a depth test! Before we do that, let's view the contents of the depth buffer. Change the fragment shader temporarily.\
In fragment.txt:
```
#version 330 core

in vec3 fragmentColor;

out vec4 color;

void main()
{
    color = vec4(vec3(gl_FragCoord.z), 1.0);
}
```

Now if we run this, we can see that the depth buffer goes from 0 to 1, where 0 is closer and 1 is further, now let's enable depth testing and choose an appropriate depth test.

In Renderer's set_up_opengl function:
```python
glEnable(GL_DEPTH_TEST)
glDepthFunc(GL_LESS)
```

Think of each pixel like a bin, to draw a pixel, we throw new information in the bin, but before we do that, we can check what's in the bin already. More specifically, we only want to overwrite an existing pixel if we're overwriting it with a pixel with a lesser depth value. There's one thing we need to do as well,

In Renderer's render function:
```python
glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
```

We want to clear the color buffer as well as the depth buffer. Here we're using bitwise "or" to specify that we're clearing both buffers. This uses a bitmask pattern, similar to the way we handle key input for walking. If we ctrl+click into the definition we can see that these are special constants for OpenGL:
```python
GL_COLOR_BUFFER_BIT=_C('GL_COLOR_BUFFER_BIT',0x00004000)
GL_DEPTH_BUFFER_BIT=_C('GL_DEPTH_BUFFER_BIT',0x00000100)
```
So in other words, GL_COLOR_BUFFER_BIT, is a special bit pattern which refers just to the color buffer! (When I was learning this stuff for the first time that always confused me. "Yes, but I don't want to clear a bit, I want to clear the whole buffer!"). Anyway, so we can revert the fragment shader to its original and confirm that the program is using depth testing appropriately.

### 2: Transparency

Now let's get transparency working, and see how order affects it. Say we have some meshes with RGBA colors, and they pass that color to a uniform when rendering (rather than per vertex), this is easy enough to implement.\
In fragment.txt:
```
#version 330 core

uniform vec4 objectColor;

out vec4 color;

void main()
{
    color = objectColor;
}
```

Save that, and run the program and...
and...

no change! It turns out alpha blending must be enabled, let's go ahead and set that.\
In Renderer's set_up_opengl function:

```python
glEnable(GL_BLEND)
```
And now we can run it, and, still nothing. We also need to specify a blend function. The blend function based on the linear combination:
```
destination_color = source_color * source_factor 
                    + destination_color * destination_factor
```
Here the source is the incoming fragment and destination is the existing fragment in the colorbuffer. The coefficients are set in OpenGL by the function:
```
glBlendFunc(GLenum sfactor, GLenum dfactor)
```
So for traditional alpha blending we want
```
result_color = source_color * source_alpha + destination_color * (1 - source_alpha)
```
let's add that.\
In Renderer's set_up_opengl function:
```python
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
```
And now alpha blending is working! Let's investigate an interesting edge case though.

### Transparency is not order-independent
Open up the finished folder in the transparency section, try reversing the rectangles in the scene, does it affect the appearance of the objects?\
Implementing proper order independent transparency might be an interesting topic to include in a project. A quick workaround is to simply have the renderer simply draw all the opaque objects first, then all the transparent ones, and maybe order transparent objects via some heuristic.

### Bonus: Level of Detail
A common performance optimisation in games is level of detail for meshes. As objects get further away, they're drawn with low poly meshes. Load up the LOD folder and run the program. Tweak the level of detail function get_level in the renderer class until the mesh is optimal on your system.

### Bonus: Alise and the Madness of Cubism
Here's a demo that uses a lot of the concepts we've been looking at so far, plus a preview of textures (next week's prac). Load it up and enjoy!
Controls: 
- WASD to move
- space to jump, hold space to hover
- right click to zoom in, left click to zoom out.