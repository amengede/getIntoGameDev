#include "renderer.h"
#include "device.h"
#include "shader.h"
#include "command.h"
#include "sychronisation.h"
#include <sstream>

Engine::Engine(GLFWwindow* window) :
	window(window) {

	logger = Logger::get_logger();
	//logger->set_mode(false);
	logger->print("Made a graphics engine");

	instance = make_instance("Real Engine", instanceDeletionQueue);
	dldi = vk::DispatchLoaderDynamic(instance, vkGetInstanceProcAddr);
	if (logger->is_enabled()) {
		debugMessenger = logger->make_debug_messenger(instance, dldi, instanceDeletionQueue);
	}

	VkSurfaceKHR raw_surface;
	glfwCreateWindowSurface(instance, window, nullptr, &raw_surface);
	surface = raw_surface;
	instanceDeletionQueue.push_back([this](vk::Instance instance) {
		instance.destroySurfaceKHR(surface);
		});

	physicalDevice = choose_physical_device(instance);

	logger->set_mode(true);
	logicalDevice = create_logical_device(
		physicalDevice, surface, deviceDeletionQueue);
	uint32_t graphicsQueueFamilyIndex = find_queue_family_index(
		physicalDevice, surface, vk::QueueFlagBits::eGraphics);
	graphicsQueue = logicalDevice.getQueue(graphicsQueueFamilyIndex, 0);

	int width, height;
	glfwGetWindowSize(window, &width, &height);
	swapchain.build(
		logicalDevice, physicalDevice, surface, width, height,
		deviceDeletionQueue);

	std::vector<vk::Image> images =
		logicalDevice.getSwapchainImagesKHR(swapchain.chain).value;

	for (uint32_t i = 0; i < images.size(); ++i) {
		frames.push_back(
			Frame(images[i], logicalDevice,
				swapchain.format.format, deviceDeletionQueue));
	}

	shaders = make_shader_objects(logicalDevice,
		"shader", dldi,
		deviceDeletionQueue);

	commandPool = make_command_pool(logicalDevice, graphicsQueueFamilyIndex,
		deviceDeletionQueue);

	for (uint32_t i = 0; i < images.size(); ++i) {
		frames[i].set_command_buffer(
			allocate_command_buffer(logicalDevice, commandPool), shaders, swapchain.extent, dldi);
	}

	imageAquiredSemaphore = make_semaphore(logicalDevice, deviceDeletionQueue);
	renderFinishedSemaphore = make_semaphore(logicalDevice, deviceDeletionQueue);
	renderFinishedFence = make_fence(logicalDevice, deviceDeletionQueue);

	currentTime = glfwGetTime();
	lastTime = currentTime;
	numFrames = 0;
}

void Engine::draw() {

	//Wait for a possible render operation, then reset it so
	// that it can be signalled by this frame's render
	logicalDevice.waitForFences(renderFinishedFence, false, UINT64_MAX);
	logicalDevice.resetFences(renderFinishedFence);

	//Send an asynchronous fetch request for an image index on the swapchain,
	// the imageAquiredSemaphore will be signalled upon completion
	uint32_t imageIndex = logicalDevice.acquireNextImageKHR(
		swapchain.chain, UINT64_MAX, imageAquiredSemaphore, nullptr).value;

	//Graphics operations! Wait upon image aquisition, and signal 
	// the renderFinishedSemaphore upon completion
	vk::SubmitInfo submitInfo = {};
	submitInfo.commandBufferCount = 1;
	submitInfo.pCommandBuffers = &frames[imageIndex].commandBuffer;
	submitInfo.waitSemaphoreCount = 1;
	submitInfo.pWaitSemaphores = &imageAquiredSemaphore;
	submitInfo.signalSemaphoreCount = 1;
	submitInfo.pSignalSemaphores = &renderFinishedSemaphore;
	vk::PipelineStageFlags waitStage = vk::PipelineStageFlagBits::eColorAttachmentOutput;
	submitInfo.pWaitDstStageMask = &waitStage;
	graphicsQueue.submit(submitInfo, renderFinishedFence);

	//Queue the swapchain image up for presentation, 
	// wait on the previous render operation, and
	// signal the fence upon completion
	vk::PresentInfoKHR presentInfo = {};
	presentInfo.swapchainCount = 1;
	presentInfo.pSwapchains = &swapchain.chain;
	presentInfo.pImageIndices = &imageIndex;
	presentInfo.waitSemaphoreCount = 1;
	presentInfo.pWaitSemaphores = &renderFinishedSemaphore;

	graphicsQueue.presentKHR(presentInfo);
}

void Engine::update_timing() {
	currentTime = glfwGetTime();
	double delta = currentTime - lastTime;

	if (delta >= 1) {
		int framerate{ std::max(1, int(numFrames / delta)) };
		std::stringstream title;
		title << "Render Thread running at " << framerate << " fps.";
		glfwSetWindowTitle(window, title.str().c_str());
		lastTime = currentTime;
		numFrames = -1;
		frameTime = float(1000.0 / framerate);
	}

	++numFrames;
}

Engine::~Engine() {

	graphicsQueue.waitIdle();

	logger->print("Goodbye see you!");

	while (deviceDeletionQueue.size() > 0) {
		deviceDeletionQueue.back()(logicalDevice);
		deviceDeletionQueue.pop_back();
	}

	while (instanceDeletionQueue.size() > 0) {
		instanceDeletionQueue.back()(instance);
		instanceDeletionQueue.pop_back();
	}
}