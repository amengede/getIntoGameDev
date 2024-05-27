import glfw
import glfw.GLFW as GLFW_CONSTANTS
import message_logger
from multiprocessing import Process, Manager
from multiprocessing.managers import DictProxy, ListProxy

class Engine:
    """
        Vroom vroom.
    """

    
    def __init__(self, window: "glfw.Window"):
        """
            Initialize the graphics engine.

            Parameters:

                window: the main window of the app.
        """

        
        self._logger = message_logger.logger
        self._logger.log("Made a graphics engine")

        self._window = window

    def close(self):

        self._logger.log("Goodbye see you!\n")

def build_glfw_window(size: tuple[int]) -> "glfw.Window":
    """
        builds and returns a window.

        Parameters:

            size: width, height
    """

    width, height = size
    name = "ID Tech 12"
    logger = message_logger.logger

    glfw.init()

    #no default rendering client, we'll hook vulkan up to the window later
    glfw.window_hint(GLFW_CONSTANTS.GLFW_CLIENT_API, GLFW_CONSTANTS.GLFW_NO_API)
    #resizing breaks the swapchain, we'll disable it for now
    glfw.window_hint(GLFW_CONSTANTS.GLFW_RESIZABLE, GLFW_CONSTANTS.GLFW_FALSE)
    
    #create_window(int width, int height, const char *title, GLFWmonitor *monitor, GLFWwindow *share)
    window = glfw.create_window(width, height, name, None, None)
    if window is not None:
        logger.log(f"Successfully made a glfw window called \"{name}\", width: {width}, height: {height}\n")
    else:
        logger.log("GLFW window creation failed\n")
    
    return window

def spawn_render_thread(context: DictProxy) -> None:
    """
        Spawns the rendering thread.

        Parameters:

            context: holds shared state.
    """

    window = context["window"]
    engine = Engine(window)
    engine.close()

if __name__ == "__main__":

    message_logger.logger.set_mode(True)

    window_size = (800, 600)
    window = build_glfw_window(window_size)

    with Manager() as manager:
        context = manager.dict()
        context["window"] = window

        process = Process(target = spawn_render_thread, args = (context,))
        process.start()
        process.join()
    
    glfw.terminate()