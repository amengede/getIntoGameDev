from config import *
import instance
import logging
import device
import swapchain
import frame
import pipeline
import framebuffer
import commands
import sync

class Engine:

    
    def __init__(self, width, height, window, debug):

        
        #whether to print debug messages in functions
        self.debugMode = debug

        #glfw window parameters
        self.width = width
        self.height = height

        self.window = window

        if self.debugMode:
            print("Making a graphics engine")
        
        self.make_instance()
        self.make_device()
        self.make_pipeline()
        self.finalize_setup()
    
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
        self.maxFramesInFlight = len(self.swapchainFrames)
        self.frameNumber = 0

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
    
    def finalize_setup(self):

        framebufferInput = framebuffer.framebufferInput()
        framebufferInput.device = self.device
        framebufferInput.renderpass = self.renderpass
        framebufferInput.swapchainExtent = self.swapchainExtent
        framebuffer.make_framebuffers(
            framebufferInput, self.swapchainFrames, self.debugMode
        )

        commandPoolInput = commands.commandPoolInputChunk()
        commandPoolInput.device = self.device
        commandPoolInput.physicalDevice = self.physicalDevice
        commandPoolInput.surface = self.surface
        commandPoolInput.instance = self.instance
        self.commandPool = commands.make_command_pool(
            commandPoolInput, self.debugMode
        )

        commandbufferInput = commands.commandbufferInputChunk()
        commandbufferInput.device = self.device
        commandbufferInput.commandPool = self.commandPool
        commandbufferInput.frames = self.swapchainFrames
        self.mainCommandbuffer = commands.make_command_buffers(
            commandbufferInput, self.debugMode
        )

        for frame in self.swapchainFrames:
            frame.inFlight = sync.make_fence(self.device, self.debugMode)
            frame.imageAvailable = sync.make_semaphore(self.device, self.debugMode)
            frame.renderFinished = sync.make_semaphore(self.device, self.debugMode)

    def record_draw_commands(self, commandBuffer, imageIndex):

        beginInfo = VkCommandBufferBeginInfo()

        try:
            vkBeginCommandBuffer(commandBuffer, beginInfo)
        except:
            if self.debugMode:
                print("Failed to begin recording command buffer")
        
        renderpassInfo = VkRenderPassBeginInfo(
            renderPass = self.renderpass,
            framebuffer = self.swapchainFrames[imageIndex].framebuffer,
            renderArea = [[0,0], self.swapchainExtent]
        )
        
        clearColor = VkClearValue([[1.0, 0.5, 0.25, 1.0]])
        renderpassInfo.clearValueCount = 1
        renderpassInfo.pClearValues = ffi.addressof(clearColor)
        
        vkCmdBeginRenderPass(commandBuffer, renderpassInfo, VK_SUBPASS_CONTENTS_INLINE)
        
        vkCmdBindPipeline(commandBuffer, VK_PIPELINE_BIND_POINT_GRAPHICS, self.pipeline)
        
        vkCmdDraw(
            commandBuffer = commandBuffer, vertexCount = 3, 
            instanceCount = 1, firstVertex = 0, firstInstance = 0
        )
        
        vkCmdEndRenderPass(commandBuffer)
        
        try:
            vkEndCommandBuffer(commandBuffer)
        except:
            if self.debugMode:
                print("Failed to end recording command buffer")
    
    def render(self):

        #grab instance procedures
        vkAcquireNextImageKHR = vkGetDeviceProcAddr(self.device, 'vkAcquireNextImageKHR')
        vkQueuePresentKHR = vkGetDeviceProcAddr(self.device, 'vkQueuePresentKHR')

        vkWaitForFences(
            device = self.device, fenceCount = 1, pFences = [self.swapchainFrames[self.frameNumber].inFlight,], 
            waitAll = VK_TRUE, timeout = 1000000000
        )
        vkResetFences(
            device = self.device, fenceCount = 1, pFences = [self.swapchainFrames[self.frameNumber].inFlight,]
        )

        imageIndex = vkAcquireNextImageKHR(
            device = self.device, swapchain = self.swapchain, timeout = 1000000000, 
            semaphore = self.swapchainFrames[self.frameNumber].imageAvailable, fence = VK_NULL_HANDLE
        )

        commandBuffer = self.swapchainFrames[self.frameNumber].commandbuffer
        vkResetCommandBuffer(commandBuffer = commandBuffer, flags = 0)
        self.record_draw_commands(commandBuffer, imageIndex)

        submitInfo = VkSubmitInfo(
            waitSemaphoreCount = 1, pWaitSemaphores = [self.swapchainFrames[self.frameNumber].imageAvailable,], 
            pWaitDstStageMask=[VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT,],
            commandBufferCount = 1, pCommandBuffers = [commandBuffer,], signalSemaphoreCount = 1,
            pSignalSemaphores = [self.swapchainFrames[self.frameNumber].renderFinished,]
        )

        try:
            vkQueueSubmit(
                queue = self.graphicsQueue, submitCount = 1, 
                pSubmits = submitInfo, fence = self.swapchainFrames[self.frameNumber].inFlight
            )
        except:
            if self.debugMode:
                print("Failed to submit draw commands")
        
        presentInfo = VkPresentInfoKHR(
            waitSemaphoreCount = 1, pWaitSemaphores = [self.swapchainFrames[self.frameNumber].renderFinished,],
            swapchainCount = 1, pSwapchains = [self.swapchain,],
            pImageIndices = [imageIndex,]
        )
        vkQueuePresentKHR(self.presentQueue, presentInfo)

        self.frameNumber = (self.frameNumber + 1) % self.maxFramesInFlight

    def close(self):

        vkDeviceWaitIdle(self.device)

        if self.debugMode:
            print("Goodbye see you!\n")

        vkDestroyCommandPool(self.device, self.commandPool, None)

        vkDestroyPipeline(self.device, self.pipeline, None)
        vkDestroyPipelineLayout(self.device, self.pipelineLayout, None)
        vkDestroyRenderPass(self.device, self.renderpass, None)
        
        for frame in self.swapchainFrames:
            vkDestroyImageView(
                device = self.device, imageView = frame.image_view, pAllocator = None
            )
            vkDestroyFramebuffer(
                device = self.device, framebuffer = frame.framebuffer, pAllocator = None
            )
            vkDestroyFence(self.device, frame.inFlight, None)
            vkDestroySemaphore(self.device, frame.imageAvailable, None)
            vkDestroySemaphore(self.device, frame.renderFinished, None)
        
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