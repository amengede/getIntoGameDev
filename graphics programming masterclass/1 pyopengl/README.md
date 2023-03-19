### Introduction
Welcome to the PyOpenGL pracs! These sessions are a crash course covering the fundamentals of graphics programming.

### What is OpenGL?
Graphics cards are pretty powerful devices, and their drivers are their own mini operating systems. For this reason, application developers communicate with their graphics cards using APIs (Application Programming Interfaces), in the past the two most common were Directx and OpenGL. Nowdays there are new shiny toys like Vulkan, Metal and Directx 12, but those are a lot more complicated and they still build on the concepts of their ancestors. The basic idea is a graphics API sits as a communication interface with the underlying video hardware.

### What will we learn?
Graphics programming is pretty large, in my own opinion this is the sort of progression that is typical in learning it:

- Beginner (How does this thing even work?):
    - Importing libraries, getting a feel for the environment, drawing a window with a filled background colour
    - Storing vertices in memory, writing a first shader and drawing a triangle
    - Loading in textures
    - Using linear algebra to apply transformations
    - Loading Obj models (even if it's just a cube, writing vertex lists by hand is not fun)
    - Sampling Cubemaps (a surprisingly easy way to add detail to scenes)
- Intermediate (This is fun! Now how do I...):
    - Lighting (including multiple lights)
    - Billboards
    - Getting multiple shaders running at the same time
    - Framebuffers/Simple Post Processing effects
    - Text
    - Materials (composite textures consisting of Diffuse maps, Normal maps, specular maps, heightmaps etc)
- Advanced (Cool effects, and starting to render in more creative/optimised ways):
    - Bloom
    - Shadows
    - Stencil Buffer
    - Instanced Rendering
    - Deferred Shading
    - Screen Space Ambient Occlusion
    - ...
- Ray Tracing
    - ...and then you're just ray tracing for the rest of your life.

These practical sessions will mostly be focusing on the Beginner and Intermediate topics. It's going to be a busy few weeks so for now if you can understand the linear algebra involved in these labs and write some shaders then that's an awesome start. You are highly encouraged (and will be expected) to extend on the content of these labs, whether that's trying something new or extending something covered.

### One more thing
Ask questions! Let me break the fourth wall for a second and speak as Andrew, the human on planet earth. I think it's so cool that you're learning graphics programming and I want to do my best to help you but sometimes I forget what it's like to come in from maybe zero experience. Please stop me at any point and ask questions. Please go full jazz hands on this code, improvise, break it, fix it and learn.

### What Operating System can I use?
These pracs are going to be demonstrated in Visual Studio Code running Python, provided your environment can run those it should be fine. We haven't tested every niche Linux-like system but the code runs in MacOS on Apple Silicon, so no need to worry about that.

### What Development Environment can I use?
Visual Studio is probably the easiest to use, besides that the only issue we've found is Anaconda. There appears to be some fundamental version incompatibility between Anaconda and the Numpy ABI (Application Binary Interface) that PyOpenGL expects. So the moral here is don't use Anaconda for these pracs.\
Also regarding Python versions: the latest is Python 3.11, in which some major optimizations were made to the Python Interpreter. Unfortunately there do appear to be incompatibilites as third party libraries haven't caught up yet (as of writing this), so for stability purposes we'll be sticking to Python 3.10

### Overview of Libraries:
In our sessions we'll be using a few libaries, they can all be pip installed.
- [pyOpenGL](http://pyopengl.sourceforge.net/): handles OpenGL up to 4.4, including extensions. The standard install includes PyOpenGL accelerate, which, it seems, is just designed to spit out an error message every time the program runs. All jokes aside, it seems to be built for an older version of numpy, and hasn't been updated. I've heard that rolling back numpy to some previous version fixes the issue, but that's never really worked in my experience. Also, it doesn't really break the program besides the error message.
- [numpy](https://numpy.org/): Two major use cases here,
    1. Standard lists and tuples in python don't work in pyOpenGL. Long story short, it's because Python has composite data types, even a floating point number isn't a float, it's float class. Numpy converts and stores these weird frankenstein types into arrays of simple numbers, just the way our graphics card likes it.
    1. Linear algebra, vectors and matrices for transformations.
- [pyrr](https://pyrr.readthedocs.io/en/latest/): Numpy is great for making matrices, but if there's no single function to create, for example, a rotation transformation. Pyrr is a wrapper around numpy which is extremely useful for making all sorts of transformations. The library is also very readable, so you can navigate into the source code and see exactly how they use numpy to build transformations.
- [pygame](https://www.pygame.org/news): The last thing we need is a windowing library, to make a window we can draw to, and handle key and mouse input. The two major options are GLFW or SDL, they are essentially equivalent, although in my experience I find GLFW is a little easier to use with C++ and Pygame/SDL is a little easier to use with Python. Pygame is a Python wrapper around SDL (simple direct media layer). Side note, Unreal engine also uses SDL.

There are also some optional libraries if you're comfortable and want to try new things:
- [glfw](https://pypi.org/project/glfw/): These code snippets will be switching between Pygame and GLFW. Why? Don't they do the same thing? Basically yes, however Pygame measures the mouse coordinate in integers whereas glfw uses double precision floating point decimals, this means GLFW will give smoother mouse controls.
- [Pillow](https://pillow.readthedocs.io/en/stable/): The benefit of Pygame is it does more than just give us a window and use controls, it also loads images, plays sounds etc. When we switch to GLFW we'll need an image loading library.
- [numba](https://numba.pydata.org/): Totally optional, and we won't be using this in pracs, but just something to be aware of. If you want high performance Python code, numba is a just-in-time (jit) compiler that can be invoked on individual functions. If you have a single piece of code that processes a large data set, compiling it can make a lot of difference.

To start with, let's install some libraries, run the following commands in your Python development environment:
```python
pip install PyOpenGL PyOpenGL_accelerate
```
```python
pip install numpy
```
```python
pip install pyrr
```
```python
pip install pygame
```
With that out of the way, we should be ready for the prac exercises!