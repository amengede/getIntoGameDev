from config import *
import instance
import logging
import device
import swapchain
import frame
import pipeline

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
        self.make_pipeline()

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

        c_style_surface = ffi.new("VkSurfaceKHR*")
        if (
            glfw.create_window_surface(
                instance = self.instance, window = self.window, 
                allocator = None, surface = c_style_surface
            ) != VK_SUCCESS
        ):
            if self.debugMode:
                print("Failed to abstract glfw's surface for vulkan")
        elif self.debugMode:
            print("Successfully abstracted glfw's surface for vulkan")
        self.surface = c_style_surface[0]
    
    def make_device(self):

        self.physicalDevice = device.choose_physical_device(self.instance, self.debugMode)
        self.device = device.create_logical_device(
            physicalDevice = self.physicalDevice, instance = self.instance, 
            surface = self.surface, debug = self.debugMode
        )
        queues = device.get_queues(
            physicalDevice = self.physicalDevice, logicalDevice = self.device, 
            instance = self.instance, surface = self.surface,
            debug = self.debugMode
        )
        self.graphicsQueue = queues[0]
        self.presentQueue = queues[1]
        
        bundle = swapchain.create_swapchain(
            self.instance, self.device, self.physicalDevice, self.surface,
            self.width, self.height, self.debugMode
        )

        self.swapchain = bundle.swapchain
        self.swapchainFrames = bundle.frames
        self.swapchainFormat = bundle.format
        self.swapchainExtent = bundle.extent

    def make_pipeline(self):

        inputBundle = pipeline.InputBundle(
            device = self.device,
            swapchainImageFormat = self.swapchainFormat,
            swapchainExtent = self.swapchainExtent,
            vertexFilepath = "shaders/vert.spv",
            fragmentFilepath = "shaders/frag.spv"
        )

        outputBundle = pipeline.create_graphics_pipeline(inputBundle, self.debugMode)

        self.pipelineLayout = outputBundle.pipelineLayout
        self.renderpass = outputBundle.renderPass
        self.pipeline = outputBundle.pipeline

    def close(self):

        if self.debugMode:
            print("Goodbye see you!\n")

        vkDestroyPipeline(self.device, self.pipeline, None)
        vkDestroyPipelineLayout(self.device, self.pipelineLayout, None)
        vkDestroyRenderPass(self.device, self.renderpass, None)
        
        for frame in self.swapchainFrames:
            vkDestroyImageView(
                device = self.device, imageView = frame.image_view, pAllocator = None
            )
        
        destructionFunction = vkGetDeviceProcAddr(self.device, 'vkDestroySwapchainKHR')
        destructionFunction(self.device, self.swapchain, None)
        vkDestroyDevice(
            device = self.device, pAllocator = None
        )
        
        destructionFunction = vkGetInstanceProcAddr(self.instance, "vkDestroySurfaceKHR")
        destructionFunction(self.instance, self.surface, None)
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