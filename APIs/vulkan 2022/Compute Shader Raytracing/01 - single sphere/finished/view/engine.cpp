#include "engine.h"
#include "vkInit/instance.h"
#include "vkInit/device.h"
#include "vkInit/swapchain.h"
#include "vkInit/pipeline.h"
#include "vkInit/compute_pipeline.h"
#include "vkInit/framebuffer.h"
#include "vkInit/commands.h"
#include "vkInit/sync.h"
#include "vkInit/descriptors.h"
#include "vkMesh/mesh.h"
#include "vkMesh/obj_mesh.h"

Engine::Engine(int width, int height, GLFWwindow* window) {

	this->width = width;
	this->height = height;
	this->window = window;

	vkLogging::Logger::get_logger()->print("Making a graphics engine...");
	make_instance();
	make_device();
	make_descriptor_set_layouts();
	make_pipelines();
	finalize_setup();
	make_assets();
}

void Engine::make_instance() {

	instance = vkInit::make_instance("ID Tech 12");
	dldi = vk::DispatchLoaderDynamic(instance, vkGetInstanceProcAddr);
	if (vkLogging::Logger::get_logger()->get_debug_mode()) {
		debugMessenger = vkLogging::make_debug_messenger(instance, dldi);
	}
	VkSurfaceKHR c_style_surface;
	if (glfwCreateWindowSurface(instance, window, nullptr, &c_style_surface) != VK_SUCCESS) {
		vkLogging::Logger::get_logger()->print("Failed to abstract glfw surface for Vulkan.");
	}
	else {
		vkLogging::Logger::get_logger()->print(
			"Successfully abstracted glfw surface for Vulkan.");
	}
	//copy constructor converts to hpp convention
	surface = c_style_surface;
}

void Engine::make_device() {
	physicalDevice = vkInit::choose_physical_device(instance);;
	device = vkInit::create_logical_device(physicalDevice, surface);
	std::array<vk::Queue,2> queues = vkInit::get_queues(physicalDevice, device, surface);
	graphicsQueue = queues[0];
	presentQueue = queues[1];
	make_swapchain();
	frameNumber = 0;
}

/**
* Make a swapchain
*/
void Engine::make_swapchain() {
	vkInit::SwapChainBundle bundle = vkInit::create_swapchain(
		device, physicalDevice, surface, width, height
	);
	swapchain = bundle.swapchain;
	swapchainFrames = bundle.frames;
	swapchainFormat = bundle.format;
	swapchainExtent = bundle.extent;
	maxFramesInFlight = static_cast<int>(swapchainFrames.size());
	for (vkUtil::SwapChainFrame& frame : swapchainFrames) {
		frame.logicalDevice = device;
		frame.physicalDevice = physicalDevice;
		frame.width = swapchainExtent.width;
		frame.height = swapchainExtent.height;
	}

}

/**
* The swapchain must be recreated upon resize or minimization, among other cases
*/
void Engine::recreate_swapchain() {

	width = 0;
	height = 0;
	while (width == 0 || height == 0) {
		glfwGetFramebufferSize(window, &width, &height);
		glfwWaitEvents();
	}

	device.waitIdle();

	cleanup_swapchain();
	make_swapchain();
	make_framebuffers();
	make_frame_resources();
	vkInit::commandBufferInputChunk commandBufferInput = { device, commandPool, swapchainFrames };
	vkInit::make_frame_command_buffers(commandBufferInput);

}

void Engine::make_descriptor_set_layouts() {

	//Binding once per frame
	vkInit::descriptorSetLayoutData bindings;
	bindings.count = 1;

	bindings.indices.push_back(0);
	bindings.types.push_back(vk::DescriptorType::eCombinedImageSampler);
	bindings.counts.push_back(1);
	bindings.stages.push_back(vk::ShaderStageFlagBits::eFragment);

	frameSetLayout[pipelineType::SCREEN] = vkInit::make_descriptor_set_layout(device, bindings);

	bindings.types[0] = vk::DescriptorType::eStorageImage;
	bindings.stages[0] = vk::ShaderStageFlagBits::eCompute;

	frameSetLayout[pipelineType::RAYTRACE] = vkInit::make_descriptor_set_layout(device, bindings);

}

void Engine::make_pipelines() {

	//Raytracing
	vkInit::ComputePipelineBuilder computePipelineBuilder(device);

	computePipelineBuilder.specify_compute_shader("shaders/raytracer.spv");
	computePipelineBuilder.add_descriptor_set_layout(frameSetLayout[pipelineType::RAYTRACE]);

	vkInit::ComputePipelineOutBundle computeOutput = computePipelineBuilder.build();

	pipelineLayout[pipelineType::RAYTRACE] = computeOutput.layout;
	pipeline[pipelineType::RAYTRACE] = computeOutput.pipeline;
	computePipelineBuilder.reset();

	vkInit::PipelineBuilder pipelineBuilder(device);
	//Screen
	pipelineBuilder.specify_vertex_shader("shaders/screen_vertex.spv");
	pipelineBuilder.specify_fragment_shader("shaders/screen_fragment.spv");
	pipelineBuilder.specify_swapchain_extent(swapchainExtent);
	pipelineBuilder.clear_depth_attachment();
	pipelineBuilder.add_descriptor_set_layout(frameSetLayout[pipelineType::SCREEN]);
	pipelineBuilder.add_color_attachment(swapchainFormat, 0);

	vkInit::GraphicsPipelineOutBundle output = pipelineBuilder.build();

	pipelineLayout[pipelineType::SCREEN] = output.layout;
	renderpass[pipelineType::SCREEN] = output.renderpass;
	pipeline[pipelineType::SCREEN] = output.pipeline;
	pipelineBuilder.reset();

}

/**
* Make a framebuffer for each frame
*/
void Engine::make_framebuffers() {

	vkInit::framebufferInput frameBufferInput;
	frameBufferInput.device = device;
	frameBufferInput.renderpass = renderpass;
	frameBufferInput.swapchainExtent = swapchainExtent;
	vkInit::make_framebuffers(frameBufferInput, swapchainFrames);
}

void Engine::finalize_setup() {

	make_framebuffers();

	commandPool = vkInit::make_command_pool(device, physicalDevice, surface);

	vkInit::commandBufferInputChunk commandBufferInput = { device, commandPool, swapchainFrames };
	mainCommandBuffer = vkInit::make_command_buffer(commandBufferInput);
	vkInit::make_frame_command_buffers(commandBufferInput);

	make_frame_resources();

}

void Engine::make_frame_resources() {

	vkInit::descriptorSetLayoutData bindings;
	bindings.count = 1;
	bindings.types.push_back(vk::DescriptorType::eCombinedImageSampler);
	frameDescriptorPool[pipelineType::SCREEN] = vkInit::make_descriptor_pool(device, static_cast<uint32_t>(swapchainFrames.size()), bindings);

	bindings.types[0] = vk::DescriptorType::eStorageImage;
	frameDescriptorPool[pipelineType::RAYTRACE] = vkInit::make_descriptor_pool(device, static_cast<uint32_t>(swapchainFrames.size()), bindings);

	for (vkUtil::SwapChainFrame& frame : swapchainFrames) {

		frame.imageAvailable = vkInit::make_semaphore(device);
		frame.renderFinished = vkInit::make_semaphore(device);
		frame.inFlight = vkInit::make_fence(device);

		frame.colorBuffer = new vkImage::StorageImage(physicalDevice, device, swapchainExtent.width, swapchainExtent.height);
		frame.colorBuffer->initialize(mainCommandBuffer, graphicsQueue);
		frame.make_descriptor_resources();
		frame.descriptorSet[pipelineType::RAYTRACE] = vkInit::allocate_descriptor_set(device, frameDescriptorPool[pipelineType::RAYTRACE], frameSetLayout[pipelineType::RAYTRACE]);
		frame.descriptorSet[pipelineType::SCREEN] = vkInit::allocate_descriptor_set(device, frameDescriptorPool[pipelineType::SCREEN], frameSetLayout[pipelineType::SCREEN]);
		frame.record_write_operations();
	}

}

void Engine::make_assets() {

	//Make any assets
}

void Engine::prepare_frame(uint32_t imageIndex, Scene* scene) {

	vkUtil::SwapChainFrame& _frame = swapchainFrames[imageIndex];

	_frame.write_descriptor_set();
}

void Engine::prepare_scene(vk::CommandBuffer commandBuffer) {

	//Bind any global info.

}

void Engine::prepare_to_trace_barrier(vk::CommandBuffer commandBuffer, vk::Image image) {

	/*
	typedef struct VkImageSubresourceRange {
		VkImageAspectFlags    aspectMask;
		uint32_t              baseMipLevel;
		uint32_t              levelCount;
		uint32_t              baseArrayLayer;
		uint32_t              layerCount;
	} VkImageSubresourceRange;
	*/
	vk::ImageSubresourceRange access;
	access.aspectMask = vk::ImageAspectFlagBits::eColor;
	access.baseMipLevel = 0;
	access.levelCount = 1;
	access.baseArrayLayer = 0;
	access.layerCount = 1;

	/*
	typedef struct VkImageMemoryBarrier {
		VkStructureType            sType;
		const void* pNext;
		VkAccessFlags              srcAccessMask;
		VkAccessFlags              dstAccessMask;
		VkImageLayout              oldLayout;
		VkImageLayout              newLayout;
		uint32_t                   srcQueueFamilyIndex;
		uint32_t                   dstQueueFamilyIndex;
		VkImage                    image;
		VkImageSubresourceRange    subresourceRange;
	} VkImageMemoryBarrier;
	*/
	vk::ImageMemoryBarrier barrier;
	barrier.oldLayout = vk::ImageLayout::eUndefined;
	barrier.newLayout = vk::ImageLayout::eGeneral;
	barrier.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	barrier.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	barrier.image = image;
	barrier.subresourceRange = access;

	vk::PipelineStageFlags sourceStage, destinationStage;

	barrier.srcAccessMask = vk::AccessFlagBits::eNoneKHR;
	sourceStage = vk::PipelineStageFlagBits::eTopOfPipe;

	barrier.dstAccessMask = vk::AccessFlagBits::eMemoryWrite;
	destinationStage = vk::PipelineStageFlagBits::eComputeShader;

	commandBuffer.pipelineBarrier(sourceStage, destinationStage, vk::DependencyFlags(), nullptr, nullptr, barrier);
}

void Engine::dispatch_raytrace(vk::CommandBuffer commandBuffer, uint32_t imageIndex) {

	commandBuffer.bindPipeline(vk::PipelineBindPoint::eCompute, pipeline[pipelineType::RAYTRACE]);

	commandBuffer.bindDescriptorSets(vk::PipelineBindPoint::eCompute, pipelineLayout[pipelineType::RAYTRACE], 0, swapchainFrames[imageIndex].descriptorSet[pipelineType::RAYTRACE], nullptr);

	commandBuffer.dispatch(static_cast<uint32_t>(swapchainExtent.width / 8), static_cast<uint32_t>(swapchainExtent.height / 8), 1);

}

void Engine::enforce_barrier(vk::CommandBuffer commandBuffer, vk::Image image) {

	/*
	typedef struct VkImageSubresourceRange {
		VkImageAspectFlags    aspectMask;
		uint32_t              baseMipLevel;
		uint32_t              levelCount;
		uint32_t              baseArrayLayer;
		uint32_t              layerCount;
	} VkImageSubresourceRange;
	*/
	vk::ImageSubresourceRange access;
	access.aspectMask = vk::ImageAspectFlagBits::eColor;
	access.baseMipLevel = 0;
	access.levelCount = 1;
	access.baseArrayLayer = 0;
	access.layerCount = 1;

	/*
	typedef struct VkImageMemoryBarrier {
		VkStructureType            sType;
		const void* pNext;
		VkAccessFlags              srcAccessMask;
		VkAccessFlags              dstAccessMask;
		VkImageLayout              oldLayout;
		VkImageLayout              newLayout;
		uint32_t                   srcQueueFamilyIndex;
		uint32_t                   dstQueueFamilyIndex;
		VkImage                    image;
		VkImageSubresourceRange    subresourceRange;
	} VkImageMemoryBarrier;
	*/
	vk::ImageMemoryBarrier barrier;
	barrier.oldLayout = vk::ImageLayout::eGeneral;
	barrier.newLayout = vk::ImageLayout::eColorAttachmentOptimal;
	barrier.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	barrier.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	barrier.image = image;
	barrier.subresourceRange = access;

	vk::PipelineStageFlags sourceStage, destinationStage;

	barrier.srcAccessMask = vk::AccessFlagBits::eMemoryWrite;
	sourceStage = vk::PipelineStageFlagBits::eComputeShader;

	barrier.dstAccessMask = vk::AccessFlagBits::eNoneKHR;
	destinationStage = vk::PipelineStageFlagBits::eTopOfPipe;
	commandBuffer.pipelineBarrier(sourceStage, destinationStage, vk::DependencyFlags(), nullptr, nullptr, barrier);
}

void Engine::record_draw_commands_screen(vk::CommandBuffer commandBuffer, uint32_t imageIndex, Scene* scene) {

	vk::RenderPassBeginInfo renderPassInfo = {};
	renderPassInfo.renderPass = renderpass[pipelineType::SCREEN];
	renderPassInfo.framebuffer = swapchainFrames[imageIndex].framebuffer[pipelineType::SCREEN];
	renderPassInfo.renderArea.offset.x = 0;
	renderPassInfo.renderArea.offset.y = 0;
	renderPassInfo.renderArea.extent = swapchainExtent;

	vk::ClearValue colorClear;
	std::array<float, 4> colors = { 1.0f, 0.5f, 0.25f, 1.0f };

	std::vector<vk::ClearValue> clearValues = { {colorClear} };

	renderPassInfo.clearValueCount = clearValues.size();
	renderPassInfo.pClearValues = clearValues.data();

	commandBuffer.beginRenderPass(&renderPassInfo, vk::SubpassContents::eInline);

	commandBuffer.bindPipeline(vk::PipelineBindPoint::eGraphics, pipeline[pipelineType::SCREEN]);

	commandBuffer.bindDescriptorSets(vk::PipelineBindPoint::eGraphics, pipelineLayout[pipelineType::SCREEN], 0, swapchainFrames[imageIndex].descriptorSet[pipelineType::SCREEN], nullptr);

	commandBuffer.draw(6, 1, 0, 0);

	commandBuffer.endRenderPass();
}

void Engine::render(Scene* scene) {
	device.waitForFences(1, &(swapchainFrames[frameNumber].inFlight), VK_TRUE, UINT64_MAX);
	device.resetFences(1, &(swapchainFrames[frameNumber].inFlight));
	//acquireNextImageKHR(vk::SwapChainKHR, timeout, semaphore_to_signal, fence)
	uint32_t imageIndex;
	try {
		vk::ResultValue acquire = device.acquireNextImageKHR(
			swapchain, UINT64_MAX, 
			swapchainFrames[frameNumber].imageAvailable, nullptr
		);
		imageIndex = acquire.value;
	}
	catch (vk::OutOfDateKHRError error) {
		std::cout << "Recreate" << std::endl;
		recreate_swapchain();
		return;
	}
	catch (vk::IncompatibleDisplayKHRError error) {
		std::cout << "Recreate" << std::endl;
		recreate_swapchain();
		return;
	}
	catch (vk::SystemError error) {
		std::cout << "Failed to acquire swapchain image!" << std::endl;
	}
	//Update any descriptor sets
	prepare_frame(imageIndex, scene);
	//Compute Raytrace
	vk::CommandBuffer commandBuffer = swapchainFrames[frameNumber].commandBuffer;
	commandBuffer.reset();
	vk::CommandBufferBeginInfo beginInfo = {};
	try {
		commandBuffer.begin(beginInfo);
	}
	catch (vk::SystemError err) {
		vkLogging::Logger::get_logger()->print("Failed to begin recording command buffer!");
	}
	prepare_to_trace_barrier(commandBuffer, swapchainFrames[imageIndex].image);
	dispatch_raytrace(commandBuffer, imageIndex);
	enforce_barrier(commandBuffer, swapchainFrames[imageIndex].image);
	record_draw_commands_screen(commandBuffer, imageIndex, scene);
	try {
		commandBuffer.end();
	}
	catch (vk::SystemError err) {

		vkLogging::Logger::get_logger()->print("failed to record command buffer!");
	}
	vk::SubmitInfo submitInfo = {};
	vk::Semaphore waitSemaphores[] = { swapchainFrames[frameNumber].imageAvailable };
	vk::PipelineStageFlags waitStages[] = { vk::PipelineStageFlagBits::eColorAttachmentOutput };
	submitInfo.waitSemaphoreCount = 1;
	submitInfo.pWaitSemaphores = waitSemaphores;
	submitInfo.pWaitDstStageMask = waitStages;
	submitInfo.commandBufferCount = 1;
	submitInfo.pCommandBuffers = &commandBuffer;
	vk::Semaphore signalSemaphores[] = { swapchainFrames[frameNumber].renderFinished };
	submitInfo.signalSemaphoreCount = 1;
	submitInfo.pSignalSemaphores = signalSemaphores;
	try {
		graphicsQueue.submit(submitInfo, swapchainFrames[frameNumber].inFlight);
	}
	catch (vk::SystemError err) {
		vkLogging::Logger::get_logger()->print("failed to submit draw command buffer!");
	}
	vk::PresentInfoKHR presentInfo = {};
	presentInfo.waitSemaphoreCount = 1;
	presentInfo.pWaitSemaphores = signalSemaphores;
	vk::SwapchainKHR swapChains[] = { swapchain };
	presentInfo.swapchainCount = 1;
	presentInfo.pSwapchains = swapChains;
	presentInfo.pImageIndices = &imageIndex;
	vk::Result present;
	try {
		present = presentQueue.presentKHR(presentInfo);
	}
	catch (vk::OutOfDateKHRError error) {
		present = vk::Result::eErrorOutOfDateKHR;
	}
	if (present == vk::Result::eErrorOutOfDateKHR || present == vk::Result::eSuboptimalKHR) {
		std::cout << "Recreate" << std::endl;
		recreate_swapchain();
		return;
	}
	frameNumber = (frameNumber + 1) % maxFramesInFlight;
}

/**
* Free the memory associated with the swapchain objects
*/
void Engine::cleanup_swapchain() {

	for (vkUtil::SwapChainFrame& frame : swapchainFrames) {
		frame.destroy();
	}
	device.destroySwapchainKHR(swapchain);

	device.destroyDescriptorPool(frameDescriptorPool[pipelineType::RAYTRACE]);
	device.destroyDescriptorPool(frameDescriptorPool[pipelineType::SCREEN]);

}

Engine::~Engine() {

	device.waitIdle();

	vkLogging::Logger::get_logger()->print("Goodbye see you!");

	device.destroyCommandPool(commandPool);

	for (pipelineType pipeline_type : pipelineTypes) {
		device.destroyPipeline(pipeline[pipeline_type]);
		device.destroyPipelineLayout(pipelineLayout[pipeline_type]);
		device.destroyRenderPass(renderpass[pipeline_type]);
	}

	cleanup_swapchain();
	for (pipelineType pipeline_type : pipelineTypes) {
		device.destroyDescriptorSetLayout(frameSetLayout[pipeline_type]);
	}

	device.destroy();

	instance.destroySurfaceKHR(surface);
	if (vkLogging::Logger::get_logger()->get_debug_mode()) {
		instance.destroyDebugUtilsMessengerEXT(debugMessenger, nullptr, dldi);
	}
	/*
	* from vulkan_funcs.hpp:
	* 
	* void Instance::destroy( Optional<const VULKAN_HPP_NAMESPACE::AllocationCallbacks> allocator = nullptr,
                                            Dispatch const & d = ::vk::getDispatchLoaderStatic())
	*/
	instance.destroy();

	//terminate glfw
	glfwTerminate();
}