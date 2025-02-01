from config import *
import instance
import logging
import device

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
        self.make_instance()
        self.make_device()

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
    
    def make_instance(self):

        self.instance = instance.make_instance(self.debugMode, "ID tech 12")

        if self.debugMode:
            self.debugMessenger = logging.make_debug_messenger(self.instance)
    
    def make_device(self):

        self.physicalDevice = device.choose_physical_device(self.instance, self.debugMode)
        device.find_queue_families(self.physicalDevice, self.debugMode)

    def close(self):

        if self.debugMode:
            print("Goodbye see you!\n")
        
        if self.debugMode:
            #fetch destruction function
            destructionFunction = vkGetInstanceProcAddr(self.instance, 'vkDestroyDebugReportCallbackEXT')

            """
                def vkDestroyDebugReportCallbackEXT(
                    instance
                    ,callback
                    ,pAllocator
                ,):
            """
            destructionFunction(self.instance, self.debugMessenger, None)

        """
            from _vulkan.py:

            def vkDestroyInstance(
                instance,
                pAllocator,
            )
        """
        vkDestroyInstance(self.instance, None)

	    #terminate glfw
        glfw.terminate()

if __name__ == "__main__":

	graphicsEngine = Engine()

	graphicsEngine.close()