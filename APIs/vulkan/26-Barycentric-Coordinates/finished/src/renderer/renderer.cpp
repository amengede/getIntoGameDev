#include "renderer.h"
#include "device.h"
#include "shader.h"
#include "command.h"
#include <sstream>
#include <iostream>
#include "descriptors.h"

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

	VmaAllocatorCreateInfo allocatorInfo = {};
	allocatorInfo.device = logicalDevice;
	allocatorInfo.instance = instance;
	allocatorInfo.physicalDevice = physicalDevice;
	allocatorInfo.vulkanApiVersion = vk::makeApiVersion(1, 3, 0, 0);
	vmaCreateAllocator(&allocatorInfo, &allocator);

	int width, height;
	glfwGetFramebufferSize(window, &width, &height);
	swapchain.build(
		logicalDevice, physicalDevice, surface, width, height);

	DescriptorSetLayoutBuilder descriptorSetLayoutBuilder(logicalDevice);
	descriptorSetLayoutBuilder.add_entry(vk::ShaderStageFlagBits::eCompute, vk::DescriptorType::eStorageImage);
	clearDescriptorSetLayout = descriptorSetLayoutBuilder.build(deviceDeletionQueue);
	descriptorSetLayoutBuilder.add_entry(vk::ShaderStageFlagBits::eCompute, vk::DescriptorType::eStorageBuffer);
	rasterizeDescriptorSetLayout = descriptorSetLayoutBuilder.build(deviceDeletionQueue);

	PipelineLayoutBuilder pipelineLayoutBuilder(logicalDevice);
	pipelineLayoutBuilder.add(clearDescriptorSetLayout);
	clearPipelineLayout = pipelineLayoutBuilder.build(deviceDeletionQueue);
	pipelineLayoutBuilder.add(clearDescriptorSetLayout);
	pipelineLayoutBuilder.add(rasterizeDescriptorSetLayout);
	rasterizePipelineLayout = pipelineLayoutBuilder.build(deviceDeletionQueue);
	
	std::vector<vk::DescriptorSetLayout> layouts = { clearDescriptorSetLayout };
	shaders[0] = make_compute_shader(logicalDevice, "clear_screen", dldi,
		deviceDeletionQueue, layouts);
	layouts.push_back(rasterizeDescriptorSetLayout);
	shaders[1] = make_compute_shader(logicalDevice, "rasterize", dldi,
		deviceDeletionQueue, layouts);

	commandPool = make_command_pool(logicalDevice, graphicsQueueFamilyIndex,
		deviceDeletionQueue);

	mainCommandBuffer = allocate_command_buffer(logicalDevice, commandPool);

	std::vector<vk::DescriptorType> descriptorTypes = { vk::DescriptorType::eStorageImage };
	clearDescriptorPool = make_descriptor_pool(logicalDevice, 2, descriptorTypes.size(), 
		descriptorTypes.data(), deviceDeletionQueue);
	descriptorTypes[0] = vk::DescriptorType::eStorageBuffer;
	rasterizeDescriptorPool = make_descriptor_pool(logicalDevice, 2, descriptorTypes.size(),
		descriptorTypes.data(), deviceDeletionQueue);

	vertexBuffer = build_triangle(allocator, vmaDeletionQueue, mainCommandBuffer, graphicsQueue);

	for (uint32_t i = 0; i < 2; ++i) {
		vk::CommandBuffer commandBuffer = allocate_command_buffer(logicalDevice, commandPool);
		clearDescriptorSets[i] = allocate_descriptor_set(logicalDevice, clearDescriptorPool, clearDescriptorSetLayout);
		rasterizeDescriptorSets[i] = allocate_descriptor_set(logicalDevice, rasterizeDescriptorPool, rasterizeDescriptorSetLayout);
		frames.push_back(Frame(swapchain, logicalDevice, shaders, 
			dldi, commandBuffer, graphicsQueue, deviceDeletionQueue, 
			clearDescriptorSets[i], clearPipelineLayout, 
			rasterizeDescriptorSets[i], rasterizePipelineLayout, 
			allocator, &vertexBuffer));
	}

	currentTime = glfwGetTime();
	lastTime = currentTime;
	numFrames = 0;
}

void Engine::draw() {

	int width, height;
	glfwGetFramebufferSize(window, &width, &height);

	if (width == 0 && height == 0) {
		swapchain.outdated = true;
		return;
	}

	if (swapchain.outdated) {
		swapchain.rebuild(logicalDevice, physicalDevice, surface, window);
	}

	Frame& frame = frames[frameIndex];

	logicalDevice.waitForFences(frame.renderFinishedFence, false, UINT64_MAX);

	auto acquisition = logicalDevice.acquireNextImageKHR(
		swapchain.chain, UINT64_MAX, frame.imageAquiredSemaphore, nullptr);
	vk::Result result = acquisition.result;
	uint32_t imageIndex = acquisition.value;

	if (result == vk::Result::eErrorOutOfDateKHR) {
		swapchain.outdated = true;
		return;
	}

	logicalDevice.resetFences(frame.renderFinishedFence);

	frame.record_command_buffer(imageIndex);
	vk::SubmitInfo submitInfo = {};
	submitInfo.commandBufferCount = 1;
	submitInfo.pCommandBuffers = &frame.commandBuffer;
	submitInfo.waitSemaphoreCount = 1;
	submitInfo.pWaitSemaphores = &frame.imageAquiredSemaphore;
	submitInfo.signalSemaphoreCount = 1;
	submitInfo.pSignalSemaphores = &frame.renderFinishedSemaphore;
	vk::PipelineStageFlags waitStage = vk::PipelineStageFlagBits::eColorAttachmentOutput;
	submitInfo.pWaitDstStageMask = &waitStage;
	graphicsQueue.submit(submitInfo, frame.renderFinishedFence);

	vk::PresentInfoKHR presentInfo = {};
	presentInfo.swapchainCount = 1;
	presentInfo.pSwapchains = &swapchain.chain;
	presentInfo.pImageIndices = &imageIndex;
	presentInfo.waitSemaphoreCount = 1;
	presentInfo.pWaitSemaphores = &frame.renderFinishedSemaphore;
	result = graphicsQueue.presentKHR(presentInfo);

	if (result == vk::Result::eErrorOutOfDateKHR) {
		swapchain.outdated = true;
		return;
	}

	frameIndex = frameIndex ^ 1;
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

	while (vmaDeletionQueue.size() > 0) {
		vmaDeletionQueue.back()(allocator);
		vmaDeletionQueue.pop_back();
	}

	frames[0].free_resources();
	frames[1].free_resources();

	vmaDestroyAllocator(allocator);

	swapchain.destroy(logicalDevice);

	while (deviceDeletionQueue.size() > 0) {
		deviceDeletionQueue.back()(logicalDevice);
		deviceDeletionQueue.pop_back();
	}

	while (instanceDeletionQueue.size() > 0) {
		instanceDeletionQueue.back()(instance);
		instanceDeletionQueue.pop_back();
	}
}