# COSC3000 Practical 1:
## Introduction to PyOpenGL, basic drawing and transformations

Welcome to week 1! The goals of this week are:

- Even just get the system working. Set up our development environment, install libraries and get a window up.
- Send data to the GPU
- Write our first shader
- Draw a triangle
  
If you want to extend yourself, additional material covers:
- Transformations: how they are represented with matrices
- Uniforms: sending more data to the GPU, drawing the one triangle
at many positions.

### Task 1: Hello Window!
When learning to walk, the first steps are the most important. Open up the start folder and try to fill in the code. The purpose here is to install the necessary libraries and find any documentation that might be useful.

### Task 2: Hello Triangle!
This is actually not a trivial task, it roughly splits into two subtasks:

### Task 2.1: Making Vertex Data
We'll make a triangle object for our program.
```python
class Triangle:


    def __init__(self, shader):

        
        # x, y, z
        self.vertices = (
            -0.5, -0.5, 0.0,
             0.5, -0.5, 0.0,
             0.0,  0.5, 0.0,
        )
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vertex_count = 3
```
Note that we can define the vertices as a list or tuple, then simply convert it to a numpy array. We need to specify the data type as 32 bit float, because numpy uses 64 bit floats by default and if we do that openGL will simply draw nothing, or draw unpredictably, all while giving no error message!

```python
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
```
Next we need to send this data chunk, this vertex buffer, over to the GPU. glGenBuffers() allocates space on the GPU, and returns an unsigned integer which we can use to refer to that location. When we bind that buffer as the current array buffer we're telling openGL "Ok, when I do array buffer work, I want you to work on this particular buffer, index number (who knows, 5?)" If it helps you to understand this better, try printing self.vbo (which stands for Vertex Buffer Object), try running glGenBuffers a few times and printing out the result.

```python
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
```
It's not enough to just send the data over to the GPU, a vertex buffer by itself is just big, dumb data. We need to tell openGL how the information is packed in together and what it means. For instance, even if we're just storing positions and colors, there's many different ways to store that data. We could interleave positions with colors, or store all the positions first, then all the colors, or any number of other permutations.

glVertexAttribPointer(GLuint index, GLint size, GLenum type, GLboolean normalized, GLsizei stride, const void * pointer);

- index (GL unsigned integer): the index of the attribute. Position is attribute 0, this needs to match the shader source code
- size (GL integer): how many numbers describe the attribute. Attributes can have between 1 and 4 numbers (inclusive). Both position takes up three numbers
- type (GL enumeration): the data type. The graphics card sees only ones and zeros, it needs to know how to interpret that stream of bytes.
- normalized (GL boolean): should openGL normalize the data to the range [-1,1]? We'll probably never need this.
- stride (GL size, integer): stride is the "period" of the data in bytes. In other words, from the first x coordinate, how far will the program step to find the next x coordinate? Each vertex is 3 numbers, and each number is 32 bits (4 bytes), so the stride is 3 * 4 = 12.
- pointer (const void*): where does the data begin? A bit of bit level hackery is required to express this as a void pointer (a typeless memory offset), but don't be spooked, we're just doing that here, it doesn't come back, and when it does it always works the same way. Position starts at the start of the array, so an offset of 0 bytes.

Side note: when you're learning a big library like OpenGL, looking up documentation for functions like this is incredibly important. Probably the best way to learn is to read documentation and make high quality, clear, well documented code. From there, you learn what you practice.

The vertex array object is created and bound before the vertex buffer object, because the vertex array object will actually remember both the vertex buffer and the attributes.

For completeness, here's the full Triangle class. Note the memory freeing code.
```python
class Triangle:


    def __init__(self, shader):

        # x, y, z
        self.vertices = (
            -0.5, -0.5, 0.0,
             0.5, -0.5, 0.0,
             0.0,  0.5, 0.0
        )
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vertex_count = 3

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

    def destroy(self):
        glDeleteVertexArrays(1,(self.vao,))
        glDeleteBuffers(1,(self.vbo,))
```
### Task 2.2: Writing our first shader
Wait, I feel like I missed something...
### What's a shader?
Here's a little exercise: how would the psudocode work to draw a triangle between three points? Try tracing it out as a series of lines, getting down to the pixel level. Ok, that's not too bad, but if you want to do something more complicated like per pixel lighting calculations, pretty soon it gets rough.\
What's the answer? Multithreading. Let's say we have a program which we can invoke three times, once on each corner, so we get three corners for the price of one, then let's say we run some sort of routine to interpolate corner data down to a per-pixel level, and then dispatch each pizel to an individual core. Now we're really improving the performance.\
This is the fundamental concept of shaders. The graphics pipeline goes through a few key stages:\
\
Input Assembly -> vertex stage -> rasterizer -> fragment stage\
\
This is a greatly simplified view, but it highlights the key features we need to worry about. First the graphics card gets a bunch of data thrown at it, if it's drawing in triangle mode it'll batch data into sets of three and pass each set along.\
Then the vertex stage runs a vertex shader, the goal of this is generally to apply transformations on a per-corner level.\
After each set of three vertices signals they're complete, the rasterizer consumes that data and interpolates it. Every attribute is linearly interpolated between corners. The rasterizer works out how many fragments (pixels) need to be drawn, and dispatches each fragment (pixel) as a job on the fragment stage.\
Because of this massive parallelism, many hundreds of pixels could be rendered at the same time. Fragment shaders are the programs used for this. Each pixel is an instance of a shader core running the fragment shader that we write with the goal of calculating the color for that one pixel. It's trendy in modern graphics programming to say bad things about the rasterization pipeline, but it's still a tremendously powerful concept.

### Task 2.2: Writing our first shader
Before we can draw anything we need to write two shaders, a vertex and fragment shader. Let's make a new folder called "shaders", and in there make two new files: "vertex.txt" and "fragment.txt":

vertex.txt:
```
#version 330 core

layout (location=0) in vec3 vertexPos;

void main()
{
    gl_Position = vec4(vertexPos, 1.0);
}
```
The vertex shader is responsible for determining a point's position on screen, and generally applying any transformations if necessary. To set the position, we set openGL's inbuilt variable gl_Position. This is a 4 dimensional vector of the form (x,y,z,w), z = 0 corresponds to the triangle being at the screen's depth, w is 1 by default. What does this mean? Try changing the value once the program is complete, and seeing what happens! This will be discussed further in lecture 3, cameras and projection. Also note that the position is attribute 0, just like we defined in our attribute pointers.

```
#version 330 core

in vec3 fragmentColor;

out vec4 color;

void main()
{
    color = vec4(0.0, 0.0, 0.0, 1.0);
}
```
Fragments are pixels, the fragment shader's job is to tell openGL what colour a pixel should be, the color is a 4 dimensional vector of the form (r,g,b,a).

With those files written, we can return to our program and write a function that'll load, compile and link the shaders.

```python
from OpenGL.GL.shaders import compileProgram,compileShader
```

```python
def createShader(vertexFilepath, fragmentFilepath):

        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        return shader
```
We can treat this as a black box.

```python
#initialise opengl
glClearColor(0.1, 0.2, 0.2, 1)
self.shader = createShader("shaders/vertex.txt", "shaders/fragment.txt")
glUseProgram(self.shader)
self.triangle = Triangle()
self.mainLoop()
```
This is how we can go ahead and create our shader and triangle. The last part is to actually use them to draw!

```python
glClear(GL_COLOR_BUFFER_BIT)

glUseProgram(self.shader)
glBindVertexArray(self.triangle.vao)
glDrawArrays(GL_TRIANGLES, 0, self.triangle.vertex_count)

pg.display.flip()
```

Because the triangle vao remembers the buffer data and the attributes (ie, the stuff and what it means), it's enough to simply bind it then draw.

It's also good practice to clear any memory that was allocated (python doesn't usually allocate memory, but OpenGL does):
```python
def quit(self):
    self.triangle.destroy()
    glDeleteProgram(self.shader)
    pg.quit()
```

Run your program and observe the beautiful triangle! If your program isn't working, or you want to check your implementation, check the "finished" folder. Also don't forget to play around with that w value! tweak the line:
```
gl_Position = vec4(vertexPos, 1.0);
```
What does that last number seem to be doing?

### Extension Task
Try storing color data as well as positions, and passing that along to the shader to make a multicolored triangle. This really shows the rasterizer in action.

### Transformed Triangle
So we have a triangle, what if we want to move it? We have two options:

- Change the vertex data on the CPU, then send that updated data to the GPU
- Keep the original data, but send a transformation matrix to the GPU each frame

Let's look at both.

### Updating Vertex Data
Navigate to the folder "vertex data refresh", now we've been using a triangle, but once we start transforming things around, it's a good idea to separate the object from its representation, for that we'll make an Entity class, which will just store a position and rotation and do nothing else.
```python
class Entity:


    def __init__(self, position, eulers):

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)
```
We'll then change our Triangle class to "TriangleMesh", just a personal preference of mine. The two fundamental asset types of a renderer are meshes and materials. Combinations of the two, along with data on where and how to draw them create rendered graphics. So with this convention we could, for example, have "Triangle", "TriangleMesh" and "TriangleMaterial" classes with no issues.
Anyway, let's tweak the TriangleMesh class a little.
```python
class TriangleMesh:


    def __init__(self):

        self.originalPositions = (
            pyrr.vector4.create(-0.5, -0.5, 0.0, 1.0, dtype=np.float32),
            pyrr.vector4.create( 0.5, -0.5, 0.0, 1.0, dtype=np.float32),
            pyrr.vector4.create( 0.0,  0.5, 0.0, 1.0, dtype=np.float32)
        )

        self.originalColors = (
            pyrr.vector3.create(1.0, 0.0, 0.0, dtype=np.float32),
            pyrr.vector3.create(0.0, 1.0, 0.0, dtype=np.float32),
            pyrr.vector3.create(0.0, 0.0, 1.0, dtype=np.float32)
        )

        self.vertex_count = 3

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        self.build_vertices(pyrr.matrix44.create_identity(dtype=np.float32))

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
```
The basic idea is we want to represent the fundamental data, unchanged, then have a function that takes a transformation matrix, applies it, and sends a transformed set of the data to the GPU. This function will also have to interleave the position and color data so we have a single array holding all the data.

Here it is:
```python
def build_vertices(self, transform):

    self.vertices = np.array([],dtype=np.float32)

    for i in range(self.vertex_count):

        transformed_position = pyrr.matrix44.multiply(
            m1 = self.originalPositions[i], 
            m2 = transform
        )

        self.vertices = np.append(self.vertices, transformed_position[0:3])
        self.vertices = np.append(self.vertices, self.originalColors[i])

    glBindVertexArray(self.vao)
    glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
    glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
```
Something fishy is going on! In the initialization code, the original positions were actually 4 dimensional, with (x,y,z,1) form, this was so that translation transformations could be applied, however when appending position data to the vertex buffer, we only grab elements [0,1,2] of each vector (hence the vector slice [0:3]).

Anyway, since we're transforming on the CPU side then sending over, our shaders don't need to be modified, let's have a look at how this all comes together in the app class:

```python
class App:

    def __init__(self):
        
        ...
        glUseProgram(self.shader)

        self.triangle_mesh = TriangleMesh()

        self.triangle = Component(
            position = [0.5,0,0],
            eulers = [0,0,0]
        )

        self.mainLoop()

    def mainLoop(self):
        running = True
        while (running):
            #check events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
            
            #update triangle
            self.triangle.eulers[2] += 0.25
            if self.triangle.eulers[2] > 360:
                self.triangle.eulers[2] -= 360
            
            #refresh screen
            glClear(GL_COLOR_BUFFER_BIT)
            glUseProgram(self.shader)

            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform, 
                m2=pyrr.matrix44.create_from_y_rotation(
                    theta = np.radians(self.triangle.eulers[2]), 
                    dtype=np.float32
                )
            )
            
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform, 
                m2=pyrr.matrix44.create_from_translation(
                    vec=self.triangle.position,
                    dtype=np.float32
                )
            )

            self.triangle_mesh.build_vertices(model_transform)
            glBindVertexArray(self.triangle_mesh.vao)
            glDrawArrays(
                GL_TRIANGLES, 0, self.triangle_mesh.vertex_count
            )

            pg.display.flip()

            #timing
            self.clock.tick(60)
        self.quit()
```
We can now run this and verify that it's working. Although this method of transformations is not the most efficient, the idea of updating vertex buffer data may be useful in other cases (eg. animation tweening, Alice Liddell's hair, ...).\
<img src="./alice.jpg" width = 800>

### Using Uniforms
Open the folder "transformed triangle/uniforms" and go to the start folder. 

And, as before, we'll create a triangle and update it in the main loop.

In App's create_assets function:

```python
self.triangle_mesh = TriangleMesh()

self.triangle = Entity(
    position = [0.5,0,0],
    eulers = [0,0,0]
)
```
In the App's main loop:
```python
#update triangle
self.triangle.eulers[2] += 0.25
if self.triangle.eulers[2] > 360:
    self.triangle.eulers[2] -= 360
```

Now in our shader we need to declare a uniform (a global parameter that can be passed to the shader), here's our code:

In vertex.txt:
```
#version 330 core

layout (location=0) in vec3 vertexPos;
layout (location=1) in vec3 vertexColor;

uniform mat4 model;

out vec3 fragmentColor;

void main()
{
    gl_Position = model * vec4(vertexPos, 1.0);
    fragmentColor = vertexColor;
}
```

The fragment shader doesn't need to change at all, as moving a triangle
won't change its color:
```
#version 330 core

in vec3 fragmentColor;

out vec4 color;

void main()
{
    color = vec4(fragmentColor, 1.0);
}
```
As you can see, very little has changed, just two lines in the vertex shader. Now we need to send the model matrix to the shader, we need to fetch the uniform location from the shader, then send the data in. Since the data will be sent every frame, it makes sense to fetch the location once at initialization and store that in a variable.

In App's get_uniform_locations function:
```python
glUseProgram(self.shader)
self.modelMatrixLocation = glGetUniformLocation(self.shader,"model")
```
We have to have called glUseProgram on a shader before we fetch a location from it. Otherwise OpenGL will give us an "Invalid operation" error. Errors like this aren't always well documented.

As before, we'll build our model matrix each frame, but this time instead of using the matrix ourselves, we'll pass it over to the shader.

In the App's main loop:
```python
#refresh screen
glClear(GL_COLOR_BUFFER_BIT)
glUseProgram(self.shader)

glUniformMatrix4fv(
    self.modelMatrixLocation, 1, GL_FALSE, 
    self.triangle.make_model_transform()
)
glBindVertexArray(self.triangle_mesh.vao)
glDrawArrays(GL_TRIANGLES, 0, self.triangle_mesh.vertex_count)
```
The new function here is glUniformMatrix4fv, what are its arguments? Look it up and write a quick documenting comment.

We can now run the program and check that it works. Which method do you prefer?

### Transformation Hierarchies, Scene Graphs
One interesting use of transformations is that they can be chained together. Imagine you have objects sitting on a board, as you tilt the board you'd expect the objects to transform as well, maybe roll around the surface, right?\
So how do we achieve this? Do we perform some complicated math to find the new position in space? How about the rotation? There must be a better way!\
Consider this alternative approach, each piece on the board is a child of the board, when it comes time to calculate its transform, we first calculate the child's individual transform, then apply the parent's transform to it. In this way, transformation hierarchies and scene graphs can be built.\
I'll leave it at that, but this could be a possible topic to extend for a project (eg. skeletal animation)