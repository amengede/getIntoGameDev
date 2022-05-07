"""
    PyVulkan Tutorial
    - Stage twelve, multithreading -
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

MAX_FRAMES_IN_FLIGHT = 2

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
        self.swapchainFramebuffers = []

        self.renderPass = None
        self.pipelineLayout = None
        self.graphicsPipeline = None

        self.commandPool = None
        self.commandBuffers = None

        self.imageAvailableSemaphores = []
        self.renderFinishedSemaphores = []
        self.inFlightFences = []
        self.inFlightImages = []
        self.currentFrame = 0

        self.currentTime = 0
        self.lastTime = 0
        self.numFrames = 0

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
        self.createRenderPass()
        self.createGraphicsPipeline()
        self.createFrameBuffers()
        self.createCommandPool()
        self.createCommandBuffers()
        self.createSyncObjects()

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

    def createRenderPass(self):
        #specify the format for the color buffer
        colorAttachment = VkAttachmentDescription(
            format=self.swapchainImageFormat,
            samples=VK_SAMPLE_COUNT_1_BIT,

            loadOp=VK_ATTACHMENT_LOAD_OP_CLEAR, #operation to perform upon starting a new render pass
            storeOp=VK_ATTACHMENT_STORE_OP_STORE, #keep pixels persistent in memory after drawing

            stencilLoadOp=VK_ATTACHMENT_LOAD_OP_DONT_CARE,
            stencilStoreOp=VK_ATTACHMENT_STORE_OP_DONT_CARE, #stencil buffer isn't being used

            initialLayout=VK_IMAGE_LAYOUT_UNDEFINED,
            finalLayout=VK_IMAGE_LAYOUT_PRESENT_SRC_KHR #regardless of initial pixel format,
            #by the end of the render pass, pixels must be in an appropriate format to present onscreen.
        )

        colorAttachmentRef = VkAttachmentReference(
            attachment=0, #references colorAttachment defined above (index 0)
            layout=VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL
        )

        dependency = VkSubpassDependency(
            srcSubpass=VK_SUBPASS_EXTERNAL, #implicit render subpass depends on
            dstSubpass=0, #our subpass defined below
            srcStageMask=VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT, #operation to wait on
            srcAccessMask=0, #stage in which it occurs
            dstStageMask=VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT, #operation which waits
            dstAccessMask=VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT, #stage of operation to wait
        )

        subpass = VkSubpassDescription(
            pipelineBindPoint=VK_PIPELINE_BIND_POINT_GRAPHICS,
            colorAttachmentCount=1,
            pColorAttachments=colorAttachmentRef
        )

        renderPassInfo = VkRenderPassCreateInfo(
            sType=VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO,
            attachmentCount=1,
            pAttachments=colorAttachment,
            subpassCount=1,
            pSubpasses=subpass,
            dependencyCount=1,
            pDependencies= dependency
        )

        self.renderPass = vkCreateRenderPass(self.device, renderPassInfo, None)

    def createGraphicsPipeline(self):

        #vertex input stage
        #At this stage, no vertex data is being fetched.
        vertexInputInfo = VkPipelineVertexInputStateCreateInfo(
            sType=VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO,
            vertexBindingDescriptionCount=0,
            vertexAttributeDescriptionCount=0
        )

        #vertex shader transforms vertices appropriately
        vertexShaderModule = self.createShaderModule("shaders/vert.spv")
        vertexShaderStageInfo = VkPipelineShaderStageCreateInfo(
            sType=VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
            stage=VK_SHADER_STAGE_VERTEX_BIT,
            module=vertexShaderModule,
            pName="main"
        )

        #input assembly, which construction method to use with vertices
        inputAssembly = VkPipelineInputAssemblyStateCreateInfo(
            sType=VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO,
            topology=VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST,
            primitiveRestartEnable=VK_FALSE #allows "breaking up" of strip topologies
        )

        #transformation from image to framebuffer: stretch
        viewport = VkViewport(
            x=0,
            y=0,
            width=self.swapchainExtent.width,
            height = self.swapchainExtent.height,
            minDepth=0.0,
            maxDepth=1.0
        )

        #transformation from image to framebuffer: cutout
        scissor = VkRect2D(
            offset=[0,0],
            extent=self.swapchainExtent
        )

        #these two transformations combine to define the state of the viewport
        viewportState = VkPipelineViewportStateCreateInfo(
            sType=VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO,
            viewportCount=1,
            pViewports=viewport,
            scissorCount=1,
            pScissors=scissor
        )

        #rasterizer interpolates between vertices to produce fragments, it
        #also performs visibility tests
        raterizer = VkPipelineRasterizationStateCreateInfo(
            sType=VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO,
            depthClampEnable=VK_FALSE,
            rasterizerDiscardEnable=VK_FALSE,
            polygonMode=VK_POLYGON_MODE_FILL,
            lineWidth=1.0,
            cullMode=VK_CULL_MODE_BACK_BIT,
            frontFace=VK_FRONT_FACE_CLOCKWISE,
            depthBiasEnable=VK_FALSE #optional transform on depth values
        )

        #multisampling parameters
        multisampling = VkPipelineMultisampleStateCreateInfo(
            sType=VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO,
            sampleShadingEnable=VK_FALSE,
            rasterizationSamples=VK_SAMPLE_COUNT_1_BIT
        )

        #fragment shader takes fragments from the rasterizer and colours them
        #appropriately
        fragmentShaderModule = self.createShaderModule("shaders/frag.spv")
        fragmentShaderStageInfo = VkPipelineShaderStageCreateInfo(
            sType=VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
            stage=VK_SHADER_STAGE_FRAGMENT_BIT,
            module=fragmentShaderModule,
            pName="main"
        )

        shaderStages = [vertexShaderStageInfo, fragmentShaderStageInfo]

        #color blending, take the output from the fragment shader then incorporate it with the
        #existing pixel, if it has been set.
        colorBlendAttachment = VkPipelineColorBlendAttachmentState(
            colorWriteMask=VK_COLOR_COMPONENT_R_BIT | VK_COLOR_COMPONENT_G_BIT | VK_COLOR_COMPONENT_B_BIT | VK_COLOR_COMPONENT_A_BIT,
            blendEnable=VK_FALSE #blend function
        )
        colorBlending = VkPipelineColorBlendStateCreateInfo(
            sType=VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO,
            logicOpEnable=VK_FALSE, #logical operations
            attachmentCount=1,
            pAttachments=colorBlendAttachment,
            blendConstants=[0.0, 0.0, 0.0, 0.0]
        )

        pipelineLayoutInfo = VkPipelineLayoutCreateInfo(
            sType=VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO
        )

        self.pipelineLayout = vkCreatePipelineLayout(self.device, pipelineLayoutInfo, None)

        pipelineInfo = VkGraphicsPipelineCreateInfo(
            sType=VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO,
            stageCount=2,
            pStages=shaderStages,
            pVertexInputState=vertexInputInfo,
            pInputAssemblyState=inputAssembly,
            pViewportState=viewportState,
            pRasterizationState=raterizer,
            pMultisampleState=multisampling,
            pDepthStencilState=None,
            pColorBlendState=colorBlending,
            layout=self.pipelineLayout,
            renderPass=self.renderPass,
            subpass=0 #index to subpass 0, the only subpass
        )

        #vkCreateGraphicsPipelines(device, pipelineCache, createInfoCount, pCreateInfos, pAllocator, pPipelines=None)
        self.graphicsPipeline = vkCreateGraphicsPipelines(self.device, VK_NULL_HANDLE, 1, pipelineInfo, None)[0]

        vkDestroyShaderModule(self.device, vertexShaderModule, None)
        vkDestroyShaderModule(self.device, fragmentShaderModule, None)

    def createFrameBuffers(self):
        for imageView in self.swapchainImageViews:
            attachmants = [imageView,]

            framebufferInfo = VkFramebufferCreateInfo(
                sType=VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO,
                renderPass=self.renderPass,
                attachmentCount=1,
                pAttachments=attachmants,
                width=self.swapchainExtent.width,
                height=self.swapchainExtent.height,
                layers=1
            )

            self.swapchainFramebuffers.append(vkCreateFramebuffer(self.device, framebufferInfo, None))

    def createShaderModule(self,filepath):
        with open(filepath, 'rb') as file:
            code = file.read()
            
            createInfo = VkShaderModuleCreateInfo(
                sType=VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
                codeSize=len(code),
                pCode=code
            )
            return vkCreateShaderModule(self.device, createInfo, None)

    def createCommandPool(self):
        queueFamilyIndices = self.findQueueFamilyIndices(self.physicalDevice)

        poolInfo = VkCommandPoolCreateInfo(
            sType=VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO,
            queueFamilyIndex=queueFamilyIndices.graphicsFamily
        )

        self.commandPool = vkCreateCommandPool(self.device, poolInfo, None)

    def createCommandBuffers(self):
        allocInfo = VkCommandBufferAllocateInfo(
            sType=VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO,
            commandPool=self.commandPool,
            level=VK_COMMAND_BUFFER_LEVEL_PRIMARY,
            commandBufferCount=len(self.swapchainFramebuffers)
        )

        commandBuffers = vkAllocateCommandBuffers(self.device, allocInfo)
        self.commandBuffers = [ffi.addressof(commandBuffers, i)[0] for i in range(len(self.swapchainFramebuffers))]

        for i, commandBuffer in enumerate(self.commandBuffers):
            beginInfo = VkCommandBufferBeginInfo(
                sType=VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
                flags=VK_COMMAND_BUFFER_USAGE_SIMULTANEOUS_USE_BIT
            )

            vkBeginCommandBuffer(commandBuffer, beginInfo)

            renderPassInfo = VkRenderPassBeginInfo(
                sType=VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO,
                renderPass=self.renderPass,
                framebuffer=self.swapchainFramebuffers[i],
                renderArea=[[0, 0], self.swapchainExtent] #offset, extent
            )

            clearColor = VkClearValue([[0.2, 0.2, 0.2, 1.0]])
            renderPassInfo.clearValueCount = 1
            renderPassInfo.pClearValues = ffi.addressof(clearColor)

            vkCmdBeginRenderPass(commandBuffer, renderPassInfo, VK_SUBPASS_CONTENTS_INLINE)

            vkCmdBindPipeline(commandBuffer, VK_PIPELINE_BIND_POINT_GRAPHICS, self.graphicsPipeline)
            #vkCmdDraw(commandBuffer, vertex count, instance count, first vertex, first instance)
            vkCmdDraw(commandBuffer, 3, 1, 0, 0)

            vkCmdEndRenderPass(commandBuffer)

            vkEndCommandBuffer(commandBuffer)

    def createSyncObjects(self):
        semaphoreInfo = VkSemaphoreCreateInfo(
            sType=VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO
        )
        fenceInfo = VkFenceCreateInfo(
            sType=VK_STRUCTURE_TYPE_FENCE_CREATE_INFO,
            flags=VK_FENCE_CREATE_SIGNALED_BIT
        )

        for i in range(MAX_FRAMES_IN_FLIGHT):
            self.imageAvailableSemaphores.append(vkCreateSemaphore(self.device, semaphoreInfo, None))
            self.renderFinishedSemaphores.append(vkCreateSemaphore(self.device, semaphoreInfo, None))
            self.inFlightFences.append(vkCreateFence(self.device, fenceInfo, None))
        for i in self.swapchainImages:
            self.inFlightImages.append(VK_NULL_HANDLE)

    def mainLoop(self):
        while (not glfw.window_should_close(self.window)):
            glfw.poll_events()
            self.drawFrame()
            self.showFPS()
        vkDeviceWaitIdle(self.device)
        self.exit()

    def drawFrame(self):
        vkWaitForFences(self.device, 1, [self.inFlightFences[self.currentFrame],], VK_TRUE, 18446744073709551615)
        vkAcquireNextImageKHR = vkGetDeviceProcAddr(self.device, 'vkAcquireNextImageKHR')
        vkQueuePresentKHR = vkGetDeviceProcAddr(self.device, 'vkQueuePresentKHR')

        #aqcuire image from swapchain
        imageIndex = vkAcquireNextImageKHR(self.device, self.swapchain, 18446744073709551615, #uint64 max: disables timeout
                                           self.imageAvailableSemaphores[self.currentFrame], VK_NULL_HANDLE) #trigger imageAvailableSemaphore when image has been retrieved
        
        if (self.inFlightImages[imageIndex] != VK_NULL_HANDLE):
            vkWaitForFences(self.device, 1, [self.inFlightImages[imageIndex],], VK_TRUE, 18446744073709551615)
        self.inFlightImages[self.currentFrame] = self.inFlightFences[self.currentFrame]

        submitInfo = VkSubmitInfo(
            sType=VK_STRUCTURE_TYPE_SUBMIT_INFO,
            waitSemaphoreCount = 1,
            pWaitSemaphores = [self.imageAvailableSemaphores[self.currentFrame],], #wait on imageAvailableSemaphore before starting command queue (drawing)
            pWaitDstStageMask = [VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT,], #wait at this stage
            commandBufferCount = 1,
            pCommandBuffers = [self.commandBuffers[imageIndex],], #command buffer to execute, matches the image which was acquired for drawing 
            signalSemaphoreCount = 1,
            pSignalSemaphores = [self.renderFinishedSemaphores[self.currentFrame],] #semaphore to trigger upon queue completion
            )

        vkResetFences(self.device, 1, [self.inFlightFences[self.currentFrame],])
        vkQueueSubmit(self.graphicsQueue, 1, submitInfo, self.inFlightFences[self.currentFrame])

        swapChains = [self.swapchain,]
        presentInfo = VkPresentInfoKHR(
            sType=VK_STRUCTURE_TYPE_PRESENT_INFO_KHR,
            waitSemaphoreCount=1,
            pWaitSemaphores=[self.renderFinishedSemaphores[self.currentFrame],], #presentation waits until draw queue has finished
            swapchainCount=1,
            pSwapchains=swapChains,
            pImageIndices=[imageIndex,]
        )

        vkQueuePresentKHR(self.presentQueue, presentInfo)
        self.currentFrame = (self.currentFrame + 1) % MAX_FRAMES_IN_FLIGHT

    def showFPS(self):
        self.currentTime = glfw.get_time()
        delta = self.currentTime - self.lastTime
        if (delta >= 1):
            framerate = int(self.numFrames/delta)
            glfw.set_window_title(self.window, f"Running at {framerate}fps")
            self.numFrames = -1
            self.lastTime = self.currentTime

        self.numFrames += 1

    def exit(self):
        vkDestroySwapchainKHR = vkGetDeviceProcAddr(self.device,'vkDestroySwapchainKHR')
        vkDestroySwapchainKHR(self.device, self.swapchain, None)
        vkDestroySurfaceKHR = vkGetInstanceProcAddr(self.instance, "vkDestroySurfaceKHR")

        for i in range(MAX_FRAMES_IN_FLIGHT):
            vkDestroySemaphore(self.device, self.imageAvailableSemaphores[i], None)
            vkDestroySemaphore(self.device, self.renderFinishedSemaphores[i], None)
            vkDestroyFence(self.device, self.inFlightFences[i], None)

        vkDestroyCommandPool(self.device, self.commandPool, None)

        for framebuffer in self.swapchainFramebuffers:
            vkDestroyFramebuffer(self.device, framebuffer, None)

        vkDestroyPipeline(self.device, self.graphicsPipeline, None)
        vkDestroyPipelineLayout(self.device, self.pipelineLayout, None)
        vkDestroyRenderPass(self.device, self.renderPass, None)

        for imageView in self.swapchainImageViews:
            vkDestroyImageView(self.device, imageView, None)
        
        
        vkDestroyDevice(self.device, None)

        if (debug_mode):
            destroyDebugUtilsMessengerEXT(self.instance, self.debugMessenger, None)
        
        vkDestroySurfaceKHR(self.instance, self.surface, None)
        vkDestroyInstance(self.instance, None)
        glfw.destroy_window(self.window)
        glfw.terminate()

myApp = App()