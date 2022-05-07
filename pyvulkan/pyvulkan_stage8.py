"""
    PyVulkan Tutorial
    - Stage eight, basic shader creation -
"""
################################# imports #####################################
from vulkan import *
import glfw
import glfw.GLFW as constants
import cffi

"""
    Declare whether to run in debug mode,
    and specify the validation layers which will run.
"""
debug_mode = True
validationLayers = ["VK_LAYER_KHRONOS_validation",]

"""
    Specify the device extensions which will run.
"""
deviceExtensions = [VK_KHR_SWAPCHAIN_EXTENSION_NAME,]

"""
    Helper functions to call non-standard functions
"""
def createDebugUtilsMessengerEXT(instance, pCreateInfo, pAllocator):
    try:
        func = vkGetInstanceProcAddr(instance, "vkCreateDebugUtilsMessengerEXT")
        return func(instance, pCreateInfo, pAllocator)
    except:
        print("Couldn't find debug initialiser.")

def destroyDebugUtilsMessengerEXT(instance, debugMessenger, pAllocator):
    try:
        func = vkGetInstanceProcAddr(instance, "vkDestroyDebugUtilsMessengerEXT")
        func(instance, debugMessenger, pAllocator)
    except:
        print("Couldn't destroy debug messenger.")

#stores the indices of different queue families within vulkan
class QueueFamilyIndices:
    def __init__(self):
        # index of the graphics queue family
        self.graphicsFamily = None
        # index of the queue family for presenting graphics onscreen
        self.presentFamily = None
    
    def complete(self):
        return (self.graphicsFamily is not None) and (self.presentFamily is not None)

    def getQueues(self):
        return [self.graphicsFamily, self.presentFamily]

class SwapChainSupportDetails:
    def __init__(self):
        self.capabilities = None
        self.formats = []
        self.presentModes = []

class App:

    def __init__(self):
        self.window = None
        self.instance = None
        self.debugMessenger = None
        self.surface = None
        self.physicalDevice = VK_NULL_HANDLE
        self.device = None
        self.graphicsQueue = None
        self.presentQueue = None
        self.swapchain = None
        self.swapchainImages = None
        self.swapchainImageFormat = None
        self.swapchainExtent = None
        self.swapchainImageViews = []

        self.initWindow()
        self.initVulkan()
        self.mainLoop()
    
    def initWindow(self):
        glfw.init()

        glfw.window_hint(constants.GLFW_CLIENT_API, constants.GLFW_NO_API)
        glfw.window_hint(constants.GLFW_RESIZABLE, constants.GLFW_FALSE)
        self.width = 640
        self.height = 480

        self.window = glfw.create_window(self.width, self.height, "Vulkan Window", None, None)

    def initVulkan(self):
        self.createInstance()
        self.setupDebugMessenger()
        self.createSurface()
        self.pickPhysicalDevice()
        self.createLogicalDevice()
        self.createSwapchain()
        self.createImageViews()
        self.createGraphicsPipeline()

    def validationLayersSupported(self):
        """
            Check whether the requested validation layer/s are
            present in Vulkan's set of supported layers
        """

        try:
            availableLayers = vkEnumerateInstanceLayerProperties()
        except:
            return False
        
        for testLayer in validationLayers:
            layerFound = False
            for layerProperties in availableLayers:
                if (testLayer == layerProperties.__getattr__("layerName")):
                    layerFound = True
                    break
            
            if not layerFound:
                return False
        return True
    
    def getRequiredExtensions(self):
        """
            Return the set of extensions which glfw will need to
            run the app.
        """
        glfwExtensions = glfw.get_required_instance_extensions()
        if (debug_mode):
            glfwExtensions.append(VK_EXT_DEBUG_UTILS_EXTENSION_NAME)
        return glfwExtensions

    def debugCallback(self, *args):
        print(f"validation layer: {ffi.string(args[2].pMessage)}\n")
        return VK_FALSE

    def createInstance(self):
        if (debug_mode and not self.validationLayersSupported()):
            raise RuntimeError("validation layer/s not supported.\n")

        appInfo = VkApplicationInfo(
            sType = VK_STRUCTURE_TYPE_APPLICATION_INFO, 
            pApplicationName = "Hello Vulkan!",
            applicationVersion = VK_MAKE_VERSION(1, 0, 0),
            pEngineName = "No Engine",
            engineVersion = VK_MAKE_VERSION(1, 0, 0),
            apiVersion = VK_API_VERSION_1_0)

        extensions = self.getRequiredExtensions()
        if (debug_mode):
            layerCount = len(validationLayers)
            layerNames = validationLayers
        else:
            layerCount = 0
            layerNames = None
        
        createInfo = VkInstanceCreateInfo(
            sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            pApplicationInfo = appInfo,
            enabledExtensionCount = len(extensions),
            ppEnabledExtensionNames = extensions,
            enabledLayerCount = layerCount,
            ppEnabledLayerNames = layerNames)

        try:
            self.instance = vkCreateInstance(createInfo, None)
        except:
            raise RuntimeError("Failed to create instance!")
    
    def setupDebugMessenger(self):
        if (not debug_mode):
            return
        
        createInfo = VkDebugUtilsMessengerCreateInfoEXT(
            sType = VK_STRUCTURE_TYPE_DEBUG_UTILS_MESSENGER_CREATE_INFO_EXT,
            messageSeverity = VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT |\
                                VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT,
            messageType = VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT |\
                            VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT |\
                            VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT,
            pfnUserCallback = self.debugCallback
        )

        #load creation function
        try:
            self.debugMessenger = createDebugUtilsMessengerEXT(self.instance, createInfo, None)
        except:
            raise RuntimeError("couldn't create debugger")

    def createSurface(self):
        #glfw.create_window_surface(instance, window, allocator, surface)
        #self.surface = glfw.create_window_surface(self.instance, self.window, None, self.surface) - fails!
        surface_ptr = ffi.new('VkSurfaceKHR[1]')
        glfw.create_window_surface(self.instance, self.window, None, surface_ptr)
        self.surface = surface_ptr[0]
        if self.surface is None:
            raise RuntimeError("Failed to create window surface!")

    def pickPhysicalDevice(self):
        devices = vkEnumeratePhysicalDevices(self.instance)
        for device in devices:
            if self.deviceSuitable(device):
                self.physicalDevice = device
                break
        
        if (self.physicalDevice == VK_NULL_HANDLE):
            raise RuntimeError("Failed to find a suitable GPU!")

    def deviceSuitable(self, device):
        indices = self.findQueueFamilyIndices(device)

        swapchainAdequate = False
        extensionsSupported = self.checkDeviceExtensionSupport(device)

        if extensionsSupported:
            swapChainSupport = self.querySwapchainSupport(device)
            swapchainAdequate = len(swapChainSupport.formats) != 0 and len(swapChainSupport.presentModes) != 0 

        return indices.complete() and extensionsSupported and swapchainAdequate
    
    def checkDeviceExtensionSupport(self, device):
        # vkEnumerateDeviceExtensionProperties(device, pLayerName)
        supportedExtensions = vkEnumerateDeviceExtensionProperties(device, None)
        
        for extension in deviceExtensions:
            supported = False
            for supportedExtension in supportedExtensions:
                if (extension == supportedExtension.extensionName):
                    supported = True
            if not supported:
                return False
        return True

    def findQueueFamilyIndices(self, device):
        """ Find the first index of a queue which supports graphics and a queue which supports screen presentation"""
        indices = QueueFamilyIndices()
        vkGetPhysicalDeviceSurfaceSupportKHR = vkGetInstanceProcAddr(self.instance, 'vkGetPhysicalDeviceSurfaceSupportKHR')

        queueFamilies = vkGetPhysicalDeviceQueueFamilyProperties(device)
        i = 0
        for queueFamily in queueFamilies:
            #check graphics support
            if (queueFamily.queueFlags & VK_QUEUE_GRAPHICS_BIT):
                indices.graphicsFamily = i
            
            #check present support
            if vkGetPhysicalDeviceSurfaceSupportKHR(device, i, self.surface):
                indices.presentFamily = i
            i += 1
        return indices

    def querySwapchainSupport(self, device):
        details = SwapChainSupportDetails()

        vkGetPhysicalDeviceSurfaceCapabilitiesKHR = vkGetInstanceProcAddr(self.instance, "vkGetPhysicalDeviceSurfaceCapabilitiesKHR")
        vkGetPhysicalDeviceSurfaceFormatsKHR = vkGetInstanceProcAddr(self.instance, "vkGetPhysicalDeviceSurfaceFormatsKHR")
        vkGetPhysicalDeviceSurfacePresentModesKHR = vkGetInstanceProcAddr(self.instance, "vkGetPhysicalDeviceSurfacePresentModesKHR")

        details.capabilities = vkGetPhysicalDeviceSurfaceCapabilitiesKHR(device, self.surface)
        details.formats = vkGetPhysicalDeviceSurfaceFormatsKHR(device, self.surface)
        details.presentModes = vkGetPhysicalDeviceSurfacePresentModesKHR(device, self.surface)

        return details
    
    def chooseSwapchainSurfaceFormat(self, availableFormats):
        for format in availableFormats:
            if (format.format == VK_FORMAT_B8G8R8A8_SRGB and format.colorSpace == VK_COLOR_SPACE_SRGB_NONLINEAR_KHR):
                return format
        return availableFormats[0]

    def chooseSwapchainPresentMode(self, availablePresentModes):
        for presentMode in availablePresentModes:
            if presentMode == VK_PRESENT_MODE_MAILBOX_KHR:
                #supports triple buffering
                return presentMode
        #standard buffering, only guaranteed present mode
        return VK_PRESENT_MODE_FIFO_KHR

    def chooseSwapchainExtent(self, capabilities):
        width = max(capabilities.minImageExtent.width,min(capabilities.maxImageExtent.width,self.width))
        height = max(capabilities.minImageExtent.height,min(capabilities.maxImageExtent.height,self.height))
        return VkExtent2D(width, height)

    def createSwapchain(self):
        swapchainSupport = self.querySwapchainSupport(self.physicalDevice)

        surfaceFormat = self.chooseSwapchainSurfaceFormat(swapchainSupport.formats)
        presentMode = self.chooseSwapchainPresentMode(swapchainSupport.presentModes)
        extent = self.chooseSwapchainExtent(swapchainSupport.capabilities)

        imageCount = swapchainSupport.capabilities.minImageCount + 1
        if (swapchainSupport.capabilities.maxImageCount > 0 and imageCount > swapchainSupport.capabilities.maxImageCount):
            imageCount = swapchainSupport.capabilities.maxImageCount

        indices = self.findQueueFamilyIndices(self.physicalDevice)
        if (indices.graphicsFamily != indices.presentFamily):
            cI_imageSharingMode = VK_SHARING_MODE_CONCURRENT
            cI_queueFamilyIndexCount = 2
            cI_pQueueFamilyIndices = [indices.graphicsFamily, indices.presentFamily]
        else:
            cI_imageSharingMode = VK_SHARING_MODE_EXCLUSIVE
            cI_queueFamilyIndexCount = 0
            cI_pQueueFamilyIndices = None
        
        createInfo = VkSwapchainCreateInfoKHR(
            sType=VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR,
            surface=self.surface,
            minImageCount = imageCount,
            imageFormat=surfaceFormat.format,
            imageColorSpace=surfaceFormat.colorSpace,
            imageExtent=extent,
            imageArrayLayers=1,
            imageUsage=VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT,
            imageSharingMode = cI_imageSharingMode,
            queueFamilyIndexCount = cI_queueFamilyIndexCount,
            pQueueFamilyIndices = cI_pQueueFamilyIndices,
            preTransform = swapchainSupport.capabilities.currentTransform,
            compositeAlpha = VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR,
            presentMode = presentMode,
            clipped = VK_TRUE,
            oldSwapchain = VK_NULL_HANDLE
        )

        vkCreateSwapchainKHR = vkGetDeviceProcAddr(self.device, 'vkCreateSwapchainKHR')
        self.swapchain = vkCreateSwapchainKHR(self.device,createInfo, None)

        vkGetSwapchainImagesKHR = vkGetDeviceProcAddr(self.device, 'vkGetSwapchainImagesKHR')
        self.swapchainImages = vkGetSwapchainImagesKHR(self.device, self.swapchain)

        self.swapchainImageFormat = surfaceFormat.format
        self.swapchainExtent = extent

    def createLogicalDevice(self):
        indices = self.findQueueFamilyIndices(self.physicalDevice)
        queueCreateInfo = []
        for queue in indices.getQueues():
            queueCreateInfo.append(VkDeviceQueueCreateInfo(
                sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
                queueFamilyIndex = queue,
                queueCount = 1,
                pQueuePriorities = [1,]
            ))

        if (debug_mode):
            layerCount = len(validationLayers)
            enabledLayerNames = validationLayers
        else:
            layerCount = 0
            enabledLayerNames = None
        
        deviceFeatures = VkPhysicalDeviceFeatures()

        deviceCreateInfo = VkDeviceCreateInfo(
            sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
            flags = 0,
            pQueueCreateInfos = queueCreateInfo,
            queueCreateInfoCount = len(queueCreateInfo),
            pEnabledFeatures = deviceFeatures,
            enabledExtensionCount = len(deviceExtensions),
            ppEnabledExtensionNames = deviceExtensions,
            enabledLayerCount = layerCount,
            ppEnabledLayerNames = enabledLayerNames
        )
        try:
            self.device = vkCreateDevice(self.physicalDevice, deviceCreateInfo, None)
        except Exception as e:
            print(e)
        self.graphicsQueue = vkGetDeviceQueue(self.device, indices.graphicsFamily, 0)
        self.presentQueue = vkGetDeviceQueue(self.device, indices.presentFamily, 0)

    def createImageViews(self):
        #configure an image view for each image on the swapchain.
        for swapchainImage in self.swapchainImages:
            createInfo = VkImageViewCreateInfo(
                sType=VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO,
                image=swapchainImage,
                viewType=VK_IMAGE_VIEW_TYPE_2D,
                format=self.swapchainImageFormat,
                components=VkComponentMapping(r=VK_COMPONENT_SWIZZLE_IDENTITY, g=VK_COMPONENT_SWIZZLE_IDENTITY,
                                            b=VK_COMPONENT_SWIZZLE_IDENTITY, a=VK_COMPONENT_SWIZZLE_IDENTITY),
                subresourceRange=VkImageSubresourceRange(aspectMask=VK_IMAGE_ASPECT_COLOR_BIT,
                                                        baseMipLevel=0, levelCount=1,
                                                        baseArrayLayer=0, layerCount=1)
            )
            self.swapchainImageViews.append(vkCreateImageView(self.device,createInfo,None))
    
    def createGraphicsPipeline(self):
        vertexShaderModule = self.createShaderModule("shaders/vert.spv")
        fragmentShaderModule = self.createShaderModule("shaders/frag.spv")

        vertexShaderStageInfo = VkPipelineShaderStageCreateInfo(
            sType=VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
            stage=VK_SHADER_STAGE_VERTEX_BIT,
            module=vertexShaderModule,
            pName="main"
        )

        fragmentShaderStageInfo = VkPipelineShaderStageCreateInfo(
            sType=VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
            stage=VK_SHADER_STAGE_FRAGMENT_BIT,
            module=fragmentShaderModule,
            pName="main"
        )

        shaderStages = [vertexShaderStageInfo, fragmentShaderStageInfo]

        vkDestroyShaderModule(self.device, vertexShaderModule, None)
        vkDestroyShaderModule(self.device, fragmentShaderModule, None)
    
    def createShaderModule(self,filepath):
        with open(filepath, 'rb') as file:
            code = file.read()
            
            createInfo = VkShaderModuleCreateInfo(
                sType=VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
                codeSize=len(code),
                pCode=code
            )
            return vkCreateShaderModule(self.device, createInfo, None)

    def mainLoop(self):
        while (not glfw.window_should_close(self.window)):
            glfw.poll_events()
        self.exit()
    
    def exit(self):
        for imageView in self.swapchainImageViews:
            vkDestroyImageView(self.device, imageView, None)
        vkDestroySwapchainKHR = vkGetDeviceProcAddr(self.device,'vkDestroySwapchainKHR')
        vkDestroySwapchainKHR(self.device, self.swapchain, None)
        vkDestroySurfaceKHR = vkGetInstanceProcAddr(self.instance, "vkDestroySurfaceKHR")
        vkDestroyDevice(self.device, None)
        if (debug_mode):
            destroyDebugUtilsMessengerEXT(self.instance, self.debugMessenger, None)
        vkDestroySurfaceKHR(self.instance, self.surface, None)
        vkDestroyInstance(self.instance, None)
        glfw.destroy_window(self.window)
        glfw.terminate()

myApp = App()