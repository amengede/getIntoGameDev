import glfw
import glfw.GLFW as GLFW_CONSTANTS

#statically load vulkan library
from vulkan import *

"""
 Statically linking the prebuilt header from the lunarg sdk will load
 most functions, but not all.
 
 Functions can also be dynamically loaded, using the call
 
 PFN_vkVoidFunction vkGetInstanceProcAddr(
    VkInstance                                  instance,
    string                                      pName);

 or

 PFN_vkVoidFunction vkGetDeviceProcAddr(
	VkDevice                                    device,
	string                                      pName);

	We will look at this later, once we've created an instance and device.
"""

class Engine:

    
    def __init__(self):

        
        #whether to print debug messages in functions
        self.debugMode = True

        #glfw window parameters
        self.width = 640
        self.height = 480

        if self.debugMode:
            print("Making a graphics engine")
        
        self.build_gflw_window()

    def build_gflw_window(self):

        #initialize glfw
        glfw.init()

        #no default rendering client, we'll hook vulkan up to the window later
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CLIENT_API, GLFW_CONSTANTS.GLFW_NO_API)
        #resizing breaks the swapchain, we'll disable it for now
        glfw.window_hint(GLFW_CONSTANTS.GLFW_RESIZABLE, GLFW_CONSTANTS.GLFW_FALSE)
        
        #create_window(int width, int height, const char *title, GLFWmonitor *monitor, GLFWwindow *share)
        self.window = glfw.create_window(self.width, self.height, "ID Tech 12", None, None)
        if self.window is not None:
            if self.debugMode:
                print(f"Successfully made a glfw window called \"ID Tech 12\", width: {self.width}, height: {self.height}\n")
        else:
            if self.debugMode:
                print("GLFW window creation failed\n")

    def close(self):

        if self.debugMode:
            print("Goodbye see you!\n")

	    #terminate glfw
        glfw.terminate()

if __name__ == "__main__":

	graphicsEngine = Engine()

	graphicsEngine.close()