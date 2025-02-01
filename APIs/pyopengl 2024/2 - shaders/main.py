import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

def create_shader_program(vertex_filepath: str, fragment_filepath: str) -> int:
    """
        Compile and link a shader program.

        Parameters:

            vertex_filepath: filepath to the vertex module source code.

            fragment_filepath: filepath to the fragment module source code.

        returns:

            A handle to the created shader program.
    """

    vertex_module = create_shader_module(vertex_filepath, GL_VERTEX_SHADER)
    fragment_module = create_shader_module(fragment_filepath, GL_FRAGMENT_SHADER)

    shader = compileProgram(vertex_module, fragment_module)

    glDeleteShader(vertex_module)
    glDeleteShader(fragment_module)

    return shader

def create_shader_module(filepath: str, module_type: int) -> int:
    """
        Compile a shader module.

        Parameters:

            filepath: filepath to the module source code.

            module_type: indicates which type of module to compile.

        returns:

            A handle to the created shader module.
    """

    source_code = ""
    with open(filepath, "r") as file:
        source_code = file.readlines()

    return compileShader(source_code, module_type)

class App:


    def __init__(self):
        """ Initialise the program """

        self.initialize_glfw()
        self.initialize_opengl()

    def initialize_glfw(self) -> None:
        """
            Initialize all glfw related stuff. Make a window, basically.
        """
        glfw.init()
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR,3)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR,3)
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, 
            GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE
        )
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, 
            GLFW_CONSTANTS.GLFW_TRUE
        )
        self.window = glfw.create_window(
            SCREEN_WIDTH, SCREEN_HEIGHT, "Title", None, None)
        glfw.make_context_current(self.window)
    
    def initialize_opengl(self) -> None:
        """
            Initialize any opengl related stuff.
        """
        glClearColor(0.1, 0.2, 0.2, 1)
        self.VAO = glGenVertexArrays(1)
        self.shader = create_shader_program("shaders/vertex.txt", "shaders/fragment.txt")

    def run(self):
        """ Run the app """

        while not glfw.window_should_close(self.window):
            #check events
            if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_ESCAPE) \
                == GLFW_CONSTANTS.GLFW_PRESS:
                break
            glfw.poll_events()

            #refresh screen
            glClear(GL_COLOR_BUFFER_BIT)
            #draw triangle
            glUseProgram(self.shader)
            glBindVertexArray(self.VAO)
            glDrawArrays(GL_TRIANGLES, 0, 3)
            glfw.swap_buffers(self.window)

    def quit(self):
        """ cleanup the app, run exit code """

        glDeleteVertexArrays(1, (self.VAO,))
        glDeleteProgram(self.shader)
        glfw.destroy_window(self.window)
        glfw.terminate()

my_app = App()
my_app.run()
my_app.quit()