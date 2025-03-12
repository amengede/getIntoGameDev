#include "renderer.h"
#include "device.h"
#include "shader.h"
#include "command.h"
#include <sstream>
#include <iostream>
#include "descriptors.h"
#include "../factories/mesh_factory.h"
#include "instance.h"
#include "../backend/memory.h"
#include "../logging/logger.h"
#include <cstdlib>
#include "../math/math.h"

Engine::Engine(GLFWwindow* window) :
	window(window) {

	Logger* logger = Logger::get_logger();
	logger->print("Made a graphics engine");

	make_instance_stuff();
	logger->set_mode(false);

	make_device_stuff();

	make_allocators();

	make_descriptor_set_layouts();

	make_pipeline_layouts();

	make_shaders();

	make_command_stuff();

	make_descriptor_pools();

	load_assets();

	build_swapchain();

	timeSinceLastRender = 0.0;
	currentTime = glfwGetTime();
	lastTime = currentTime;
	numFrames = 0;
}

void Engine::make_instance_stuff() {

	Logger* logger = Logger::get_logger();

	instance = make_instance("Babalon Engine", instanceDeletionQueue);
	dldi = vk::detail::DispatchLoaderDynamic(instance, vkGetInstanceProcAddr);
	if (logger->is_enabled()) {
		debugMessenger = logger->make_debug_messenger(
			instance, dldi, instanceDeletionQueue);
	}

	VkSurfaceKHR raw_surface;
	glfwCreateWindowSurface(instance, window, nullptr, &raw_surface);
	surface = raw_surface;
	instanceDeletionQueue.push_back([this](vk::Instance instance) {
		instance.destroySurfaceKHR(surface);
	});
}

void Engine::make_device_stuff() {
	physicalDevice = choose_physical_device(instance);

	logicalDevice.device = create_logical_device(
		physicalDevice, surface, deviceDeletionQueue);
	uint32_t graphicsQueueFamilyIndex = find_queue_family_index(
		physicalDevice, surface, vk::QueueFlagBits::eGraphics);
	graphicsQueue = logicalDevice.device.getQueue(graphicsQueueFamilyIndex, 0);
}

void Engine::make_allocators() {
	mem::Allocator allocator;
	VmaAllocatorCreateInfo allocatorInfo = {};
	allocatorInfo.device = logicalDevice.device;
	allocatorInfo.instance = instance;
	allocatorInfo.physicalDevice = physicalDevice;
	allocatorInfo.vulkanApiVersion = vk::makeApiVersion(0, 1, 3, 0);
	vmaCreateAllocator(&allocatorInfo, &allocator.allocator);
	allocators[AllocatorScope::eProgram] = allocator;
	vmaCreateAllocator(&allocatorInfo, &allocator.allocator);
	allocators[AllocatorScope::eFrame] = allocator;
}

void Engine::make_descriptor_set_layouts() {

	DescriptorSetLayoutBuilder builder(logicalDevice);
	constexpr vk::ShaderStageFlags stage = vk::ShaderStageFlagBits::eCompute;
	builder.add_entry(stage, vk::DescriptorType::eStorageImage);
	DescriptorScope scope = DescriptorScope::eFrame;
	descriptorSetLayouts[scope] = builder.build();
	builder.add_entry(stage, vk::DescriptorType::eStorageBuffer);
	builder.add_entry(stage, vk::DescriptorType::eUniformBuffer);
	scope = DescriptorScope::eDrawCall;
	descriptorSetLayouts[scope] = builder.build();
	builder.add_entry(stage, vk::DescriptorType::eStorageImage);
	scope = DescriptorScope::ePost;
	descriptorSetLayouts[scope] = builder.build();
}

void Engine::make_pipeline_layouts() {

	PipelineLayoutBuilder builder(logicalDevice);

	builder.add(descriptorSetLayouts[DescriptorScope::eFrame]);
	pipelineLayouts[PipelineType::eClear] = builder.build();

	builder.add(descriptorSetLayouts[DescriptorScope::eFrame]);
	builder.add(descriptorSetLayouts[DescriptorScope::eDrawCall]);
	vk::PipelineLayout renderLayout = builder.build();
	pipelineLayouts[PipelineType::eRasterizeSmall] = renderLayout;
	pipelineLayouts[PipelineType::eRasterizeBig] = renderLayout;

	builder.add(descriptorSetLayouts[DescriptorScope::eFrame]);
	builder.add(descriptorSetLayouts[DescriptorScope::ePost]);
	pipelineLayouts[PipelineType::eWriteColor] = builder.build();
}

void Engine::make_shaders() {

	DynamicArray<vk::DescriptorSetLayout> layouts;
	layouts.push_back(descriptorSetLayouts[DescriptorScope::eFrame]);
	shaders[PipelineType::eClear] = make_compute_shader(logicalDevice,
		"clear_screen", dldi, layouts);

	layouts.push_back(descriptorSetLayouts[DescriptorScope::eDrawCall]);
	shaders[PipelineType::eRasterizeSmall] = make_compute_shader(logicalDevice,
		"rasterize_small", dldi, layouts);

	shaders[PipelineType::eRasterizeBig] = make_compute_shader(logicalDevice,
		"rasterize_big", dldi, layouts);

	layouts[1] = descriptorSetLayouts[DescriptorScope::ePost];
	shaders[PipelineType::eWriteColor] = make_compute_shader(logicalDevice,
		"write_color", dldi, layouts);
}

void Engine::make_command_stuff() {
	uint32_t graphicsQueueFamilyIndex = find_queue_family_index(
		physicalDevice, surface, vk::QueueFlagBits::eGraphics);
	commandPool = make_command_pool(logicalDevice, graphicsQueueFamilyIndex);

	mainCommandBuffer = allocate_command_buffer(logicalDevice.device, commandPool);
}

void Engine::make_descriptor_pools() {
	
	DynamicArray<vk::DescriptorType> descriptorTypes;
	descriptorTypes.push_back(vk::DescriptorType::eStorageImage);
	descriptorPools[DescriptorScope::eFrame] = make_descriptor_pool(
		logicalDevice, 2, descriptorTypes);
	
	descriptorTypes[0] = vk::DescriptorType::eStorageBuffer;
	descriptorTypes.push_back(vk::DescriptorType::eUniformBuffer);
	descriptorPools[DescriptorScope::eDrawCall] = make_descriptor_pool(
		logicalDevice, 2, descriptorTypes);
	descriptorTypes.clear();

	descriptorTypes.push_back(vk::DescriptorType::eStorageImage);
	descriptorPools[DescriptorScope::ePost] = make_descriptor_pool(
		logicalDevice, 2, descriptorTypes);
}

void Engine::load_assets() {

	int model = 0;
	mat4 preTransform;
	switch (model) {
	case 0:
		preTransform = make_translation({ 0.0f, 1.0f, 4.0f, 0.0f })
			* make_x_rotation(-90.0f)
			* make_z_rotation(80.0f)
			* make_scale(0.01f);

		vertexBuffer = build_obj_model(allocators[AllocatorScope::eProgram],
			mainCommandBuffer, graphicsQueue,
			"models/ada.obj", preTransform);
		break;

	default:
		
		preTransform = make_translation({ 0.0f, 0.0f, 30.0f, 0.0f })
			* make_x_rotation(180.0f);

		vertexBuffer = build_obj_model(allocators[AllocatorScope::eProgram],
			mainCommandBuffer, graphicsQueue,
			"models/girl2.obj", preTransform);
		break;
	}
}

void Engine::build_swapchain() {
	int width, height;
	glfwGetFramebufferSize(window, &width, &height);
	swapchain.build(
		logicalDevice.device, physicalDevice, surface, width, height);

	//Query image allignment requirement
	vk::MemoryRequirements memoryRequirements =
		logicalDevice.device.getImageMemoryRequirements(swapchain.images[0]);

	mem::ImagePoolCreateInfo imagePoolInfo;
	imagePoolInfo.allocator = allocators[AllocatorScope::eFrame].allocator;
	imagePoolInfo.blockCount = 4;
	imagePoolInfo.alignment = memoryRequirements.alignment;
	imagePoolInfo.freeAtOnce = true;
	imagePoolInfo.hostWrite = false;
	imagePoolInfo.usage = VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_STORAGE_BIT;
	allocators[AllocatorScope::eFrame].pool = mem::create_pool(imagePoolInfo);

	constexpr int frameCount = 2;
	for (uint32_t i = 0; i < frameCount; ++i) {
		vk::CommandBuffer commandBuffer =
			allocate_command_buffer(logicalDevice.device, commandPool);

		constexpr int scopeCount = 3;
		DescriptorScope scopes[scopeCount] = { 
			DescriptorScope::eFrame, DescriptorScope::eDrawCall, 
			DescriptorScope::ePost };

		for (int j = 0; j < scopeCount; ++j) {
			DescriptorScope scope = scopes[j];
			descriptorSets[i][scope] = allocate_descriptor_set(
				logicalDevice.device,
				descriptorPools[scope], descriptorSetLayouts[scope]);
		}
		frames.push_back(Frame(swapchain, logicalDevice, shaders,
			dldi, commandBuffer, graphicsQueue,
			descriptorSets[i], pipelineLayouts, &vertexBuffer,
			allocators, i));
	}
}

void Engine::draw() {

	/*
	double delta = glfwGetTime() - timeSinceLastRender;
	if (delta < (0.001 * 16.66667)) {
		return;
	}

	timeSinceLastRender = glfwGetTime();
	*/

	int width, height;
	glfwGetFramebufferSize(window, &width, &height);

	if (width == 0 && height == 0) {
		swapchain.outdated = true;
		return;
	}

	if (swapchain.outdated) {
		swapchain.rebuild(logicalDevice.device, physicalDevice, surface, window);

		graphicsQueue.waitIdle();
		allocators[AllocatorScope::eFrame].flush_deletion_queue();

		constexpr int frameCount = 2;

		for (uint32_t i = 0; i < frameCount; ++i) {
			frames[i].rebuild(&vertexBuffer);
		}
	}

	Frame& frame = frames[frameIndex];

	logicalDevice.device.waitForFences(frame.renderFinishedFence, false, UINT64_MAX);

	auto acquisition = logicalDevice.device.acquireNextImageKHR(
		swapchain.chain, UINT64_MAX, frame.imageAquiredSemaphore, nullptr);
	vk::Result result = acquisition.result;
	uint32_t imageIndex = acquisition.value;

	if (result == vk::Result::eErrorOutOfDateKHR) {
		swapchain.outdated = true;
		return;
	}

	logicalDevice.device.resetFences(frame.renderFinishedFence);

	frame.record_command_buffer(imageIndex);
	vk::SubmitInfo submitInfo = {};
	submitInfo.commandBufferCount = 1;
	submitInfo.pCommandBuffers = &frame.commandBuffer;
	submitInfo.waitSemaphoreCount = 1;
	submitInfo.pWaitSemaphores = &frame.imageAquiredSemaphore;
	submitInfo.signalSemaphoreCount = 1;
	submitInfo.pSignalSemaphores = &frame.renderFinishedSemaphore;
	vk::PipelineStageFlags waitStage = 
		vk::PipelineStageFlagBits::eColorAttachmentOutput;
	submitInfo.pWaitDstStageMask = &waitStage;
	graphicsQueue.submit(submitInfo, frame.renderFinishedFence);

	vk::PresentInfoKHR presentInfo = {};
	presentInfo.swapchainCount = 1;
	presentInfo.pSwapchains = &swapchain.chain;
	presentInfo.pImageIndices = &imageIndex;
	presentInfo.waitSemaphoreCount = 1;
	presentInfo.pWaitSemaphores = &frame.renderFinishedSemaphore;

	try {
		result = graphicsQueue.presentKHR(presentInfo);
		if (result == vk::Result::eErrorOutOfDateKHR
			|| result == vk::Result::eSuboptimalKHR) {
			swapchain.outdated = true;
			return;
		}
	}
	catch (vk::OutOfDateKHRError){
		swapchain.outdated = true;
		return;
	}

	frameIndex = frameIndex ^ 1;

	/*
	double frameTime = glfwGetTime() - timeSinceLastRender;

	std::stringstream title;
	title << "Frametime: " << float(1000.0f * frameTime) << " ms.";
	glfwSetWindowTitle(window, title.str().c_str());
	*/

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

	Logger* logger = Logger::get_logger();
	logger->print("Goodbye see you!");

	allocators[AllocatorScope::eProgram].flush_deletion_queue();
	allocators[AllocatorScope::eProgram].free();
	allocators[AllocatorScope::eFrame].flush_deletion_queue();
	allocators[AllocatorScope::eFrame].free();

	frames[0].free_resources(AllocatorScope::eFrame);
	frames[0].free_resources(AllocatorScope::eProgram);
	frames[1].free_resources(AllocatorScope::eFrame);
	frames[1].free_resources(AllocatorScope::eProgram);

	swapchain.destroy(logicalDevice.device);

	logicalDevice.free();

	while (instanceDeletionQueue.size() > 0) {
		instanceDeletionQueue.back()(instance);
		instanceDeletionQueue.pop_back();
	}
}
