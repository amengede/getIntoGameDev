from config import *

def make_window(width: int, height: int) -> "glfw.Window":
    """
        Make a GLFW window.

        Parameters:

            width, height: requested window size.
        
        Returns:

            The created window.
    """

    #initialise pygame
    glfw.init()
    glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR,3)
    glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR,3)
    glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
    glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, GLFW_CONSTANTS.GLFW_TRUE)
    #for uncapped framerate
    glfw.window_hint(GLFW_CONSTANTS.GLFW_DOUBLEBUFFER,GL_FALSE) 
    window = glfw.create_window(width, height, "Title", None, None)
    glfw.make_context_current(window)
    glfw.set_input_mode(window, GLFW_CONSTANTS.GLFW_CURSOR, GLFW_CONSTANTS.GLFW_CURSOR_HIDDEN)
    return window