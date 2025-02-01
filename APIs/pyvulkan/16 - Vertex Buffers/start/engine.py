from config import *
import instance
import logging
import device
import swapchain
import pipeline
import framebuffer
import commands
import sync

class Engine:

    
    def __init__(self, width, height, window):

        #glfw window parameters
        self.width = width
        self.height = height

        self.window = window

        logging.logger.print("Making a graphics engine")
        
        self.make_instance()
        self.make_device()
        self.make_pipeline()
        self.finalize_setup()
    
    def make_instance(self):

        self.instance = instance.make_instance("ID tech 12")

        if logging.logger.debug_mode:
            self.debugMessenger = logging.make_debug_messenger(self.instance)

        c_style_surface = ffi.new("VkSurfaceKHR*")
        if (
            glfw.create_window_surface(
                instance = self.instance, window = self.window, 
                allocator = None, surface = c_style_surface
            ) != VK_SUCCESS
        ):
            logging.logger.print("Failed to abstract glfw's surface for vulkan")
        else:
            logging.logger.print("Successfully abstracted glfw's surface for vulkan")
        self.surface = c_style_surface[0]
    
    def make_device(self):

        self.physicalDevice = device.choose_physical_device(self.instance)
        self.device = device.create_logical_device(
            physicalDevice = self.physicalDevice, instance = self.instance, 
            surface = self.surface
        )
        queues = device.get_queues(
            physicalDevice = self.physicalDevice, logicalDevice = self.device, 
            instance = self.instance, surface = self.surface,
        )
        self.graphicsQueue = queues[0]
        self.presentQueue = queues[1]
        
        self.make_swapchain()

        self.frameNumber = 0
    
    def make_swapchain(self):
        """
            Makes the engine's swapchain, note that this will make images
            and image views, it won't make frames ready for rendering.
        """

        bundle = swapchain.create_swapchain(
            self.instance, self.device, self.physicalDevice, self.surface,
            self.width, self.height
        )

        self.swapchain = bundle.swapchain
        self.swapchainFrames = bundle.frames
        self.swapchainFormat = bundle.format
        self.swapchainExtent = bundle.extent
        self.maxFramesInFlight = len(self.swapchainFrames)
    
    def recreate_swapchain(self):
        """
            Destroy the current swapchain, then rebuild a new one
        """

        self.width = 0
        self.height = 0
        while (self.width == 0 or self.height == 0):
            self.width, self.height = glfw.get_window_size(self.window)
            glfw.wait_events()

        vkDeviceWaitIdle(self.device)
        self.cleanup_swapchain()

        self.make_swapchain()
        self.make_framebuffers()
        self.make_frame_command_buffers()
        self.make_frame_sync_objects()

    def make_pipeline(self):

        inputBundle = pipeline.InputBundle(
            device = self.device,
            swapchainImageFormat = self.swapchainFormat,
            swapchainExtent = self.swapchainExtent,
            vertexFilepath = "shaders/vert.spv",
            fragmentFilepath = "shaders/frag.spv"
        )

        outputBundle = pipeline.create_graphics_pipeline(inputBundle)

        self.pipelineLayout = outputBundle.pipelineLayout
        self.renderpass = outputBundle.renderPass
        self.pipeline = outputBundle.pipeline
    
    def make_framebuffers(self):
        """
            Makes a framebuffer for each frame on the swapchain.
        """

        framebufferInput = framebuffer.framebufferInput()
        framebufferInput.device = self.device
        framebufferInput.renderpass = self.renderpass
        framebufferInput.swapchainExtent = self.swapchainExtent
        framebuffer.make_framebuffers(
            framebufferInput, self.swapchainFrames
        )
    
    def make_frame_command_buffers(self):
        """
            Make a command buffer for each frame on the swapchain.
        """

        commandbufferInput = commands.commandbufferInputChunk()
        commandbufferInput.device = self.device
        commandbufferInput.commandPool = self.commandPool
        commandbufferInput.frames = self.swapchainFrames
        commands.make_frame_command_buffers(
            commandbufferInput
        )
    
    def make_frame_sync_objects(self):
        """
            Make the semaphores and fences needed to render each frame.
        """

        for frame in self.swapchainFrames:
            frame.inFlight = sync.make_fence(self.device)
            frame.imageAvailable = sync.make_semaphore(self.device)
            frame.renderFinished = sync.make_semaphore(self.device)

    def finalize_setup(self):

        self.make_framebuffers()

        commandPoolInput = commands.commandPoolInputChunk()
        commandPoolInput.device = self.device
        commandPoolInput.physicalDevice = self.physicalDevice
        commandPoolInput.surface = self.surface
        commandPoolInput.instance = self.instance
        self.commandPool = commands.make_command_pool(
            commandPoolInput
        )

        commandbufferInput = commands.commandbufferInputChunk()
        commandbufferInput.device = self.device
        commandbufferInput.commandPool = self.commandPool
        commandbufferInput.frames = self.swapchainFrames
        self.mainCommandbuffer = commands.make_command_buffer(
            commandbufferInput
        )
        commands.make_frame_command_buffers(commandbufferInput)

        self.make_frame_sync_objects()

    def record_draw_commands(self, commandBuffer, imageIndex, scene):

        beginInfo = VkCommandBufferBeginInfo()

        try:
            vkBeginCommandBuffer(commandBuffer, beginInfo)
        except:
            logging.logger.print("Failed to begin recording command buffer")
        
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
        
        for position in scene.triangle_positions:
            
            model_transform = pyrr.matrix44.create_from_translation(vec = position, dtype = np.float32)
            #objData = ffi.cast("float *", model_transform.ctypes.data)
            objData = ffi.cast("float *", ffi.from_buffer(model_transform))
            #objData = ffi.cast("float *", model_transform.__array_interface__["data"][0])
            vkCmdPushConstants(
                commandBuffer=commandBuffer, layout = self.pipelineLayout,
                stageFlags = VK_SHADER_STAGE_VERTEX_BIT, offset = 0,
                size = 4 * 4 * 4, pValues = objData
            )
            vkCmdDraw(
                commandBuffer = commandBuffer, vertexCount = 3, 
                instanceCount = 1, firstVertex = 0, firstInstance = 0
            )
        
        vkCmdEndRenderPass(commandBuffer)
        
        try:
            vkEndCommandBuffer(commandBuffer)
        except:
            logging.logger.print("Failed to end recording command buffer")
    
    def render(self, scene):

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
        
        try:
            imageIndex = vkAcquireNextImageKHR(
                device = self.device, swapchain = self.swapchain, timeout = 1000000000, 
                semaphore = self.swapchainFrames[self.frameNumber].imageAvailable, fence = VK_NULL_HANDLE
            )
        except:
            logging.logger.print("recreate swapchain")
            self.recreate_swapchain()
            return

        commandBuffer = self.swapchainFrames[self.frameNumber].commandbuffer
        vkResetCommandBuffer(commandBuffer = commandBuffer, flags = 0)
        self.record_draw_commands(commandBuffer, imageIndex, scene)

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
            logging.logger.print("Failed to submit draw commands")
        
        presentInfo = VkPresentInfoKHR(
            waitSemaphoreCount = 1, pWaitSemaphores = [self.swapchainFrames[self.frameNumber].renderFinished,],
            swapchainCount = 1, pSwapchains = [self.swapchain,],
            pImageIndices = [imageIndex,]
        )

        try:
            vkQueuePresentKHR(self.presentQueue, presentInfo)
        except:
            logging.logger.print("recreate swapchain")
            self.recreate_swapchain()
            return

        self.frameNumber = (self.frameNumber + 1) % self.maxFramesInFlight
    
    def cleanup_swapchain(self):
        """
            Free the memory allocated for each frame, and destroy the swapchain.
        """

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

    def close(self):

        vkDeviceWaitIdle(self.device)

        logging.logger.print("Goodbye see you!\n")

        vkDestroyCommandPool(self.device, self.commandPool, None)

        vkDestroyPipeline(self.device, self.pipeline, None)
        vkDestroyPipelineLayout(self.device, self.pipelineLayout, None)
        vkDestroyRenderPass(self.device, self.renderpass, None)
        
        self.cleanup_swapchain()
        
        vkDestroyDevice(
            device = self.device, pAllocator = None
        )
        
        destructionFunction = vkGetInstanceProcAddr(self.instance, "vkDestroySurfaceKHR")
        destructionFunction(self.instance, self.surface, None)
        if logging.logger.debug_mode:
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