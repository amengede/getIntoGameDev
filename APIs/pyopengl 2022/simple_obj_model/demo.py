import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np

import os
os.environ["SDL_VIDEO_X11_FORCE_EGL"] = "1"

vec3 = list[float]

def set_up_pygame(width: int, height: int) -> None:
    """ 
         Initialize pygame and make a window.

        Parameters:

            width, height: requested window size.
    """

    pg.init()
    pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
    pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
    pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                pg.GL_CONTEXT_PROFILE_CORE)
    pg.display.set_mode((width, height), pg.OPENGL | pg.DOUBLEBUF)

def create_shader() -> int:
    """
        Create a shader, return a handle to it.
    """

    vertex_src = """
    #version 330

    layout(location=0) in vec3 vertex_position;
    layout(location=1) in vec3 vertex_color;

    out vec3 fragment_color;

    void main() {

        gl_Position = vec4(vertex_position, 1.0);

        fragment_color = vertex_color;
    }
    """

    fragment_src = """
    #version 330

    in vec3 fragment_color;

    out vec4 color;

    void main() {

        color = vec4(fragment_color, 1.0);
    }
    """

    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                            compileShader(fragment_src, GL_FRAGMENT_SHADER))

    return shader

def create_buffer_from_data(positions: list[vec3], colours: list[vec3]) -> tuple[int]:
    """
        Create a buffer, upload to it, and return handles to the resources.

        Parameters:

            positions: a list of positions

            colours: a list of colours

        Returns:
            VAO, VBO handles
    """

    # Assemble data

    data = []

    for i in range(len(positions)):
        vertex = positions[i]
        colour = colours[i]
        data.extend(vertex)
        data.extend(colour)
    data = np.array(data, dtype=np.float32)

    # Vertex Array Object: Describes whole mesh
    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)

    # Vertex Buffer Object: A data source for the mesh
    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)

    # upload data
    total_size = 4 * len(data)
    glBufferData(GL_ARRAY_BUFFER, total_size, data, GL_STATIC_DRAW)

    # describe attributes to GPU
    attribute = 0
    stride = 24 # byte size of each "vertex"
    offset = 0
    # layout(location=0) in vec3 vertex_position;
    glVertexAttribPointer(attribute, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset))
    glEnableVertexAttribArray(attribute)
    offset += 12
    attribute += 1

    # layout(location=1) in vec3 vertex_color;
    glVertexAttribPointer(attribute, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset))
    glEnableVertexAttribArray(attribute)
    offset += 4
    attribute += 1

    return VAO, VBO

def read_model(filename: str) -> list[vec3]:

    pos_data = []
    color_data = []
    pos = []
    colors = []
    file = open(filename, "r")
    
    line = file.readline()
    while line:
        
        words = line.split(" ")
        
        tag = words[0]
        if tag == "v":
            vertex = [float(words[i]) for i in range(1,4)]
            pos.append(vertex)
        if tag == "c":
            color = [float(words[i]) for i in range(1,4)]
            colors.append(color)
        if tag == "f":
            for i in range(1,4):
                v_c = [int(x) - 1 for x in words[i].split("/")]
                pos_data.append(pos[v_c[0]])
                color_data.append(colors[v_c[1]])
        line = file.readline()

    file.close()
    return pos_data, color_data

def main():
    set_up_pygame(800, 600)

    positions, colours = read_model("model.obj")

    vertex_array, buffer = create_buffer_from_data(positions, colours)
    
    shader = create_shader()

    glClearColor(0.0, 0.0, 0.0, 1.0)

    running = True
    while running:
            
        for event in pg.event.get():
            if (event.type == pg.QUIT):
                running = False

        glUseProgram(shader)
    
        glClear(GL_COLOR_BUFFER_BIT)

        glBindVertexArray(vertex_array)
        glDrawArrays(GL_TRIANGLES, 0, len(positions))

        pg.display.flip()

if __name__ == "__main__":
    main()
