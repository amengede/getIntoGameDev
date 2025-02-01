#include "renderer.h"
#include "device.h"
#include "shader.h"
#include "command.h"
#include "sychronisation.h"
#include <iostream>
#include <sstream>

Engine::Engine(GLFWwindow* window) :
	window(window) {

	logger = Logger::get_logger();
	logger->print("Made a graphics engine");
	//logger->set_mode(false);

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

	//logger->set_mode(true);
	logicalDevice = create_logical_device(
		physicalDevice, surface, deviceDeletionQueue);
	uint32_t graphicsQueueFamilyIndex = find_queue_family_index(
		physicalDevice, surface, vk::QueueFlagBits::eGraphics);
	for (uint32_t i = 0; i < 4; ++i) {
		graphicsQueues[i] = logicalDevice.getQueue(graphicsQueueFamilyIndex, i);
	}

	int width, height;
	glfwGetWindowSize(window, &width, &height);
	swapchain.build(
		logicalDevice, physicalDevice, surface, width, height,
		deviceDeletionQueue);

	shaders = make_shader_objects(logicalDevice,
		"shader", dldi,
		deviceDeletionQueue);

	commandPool = make_command_pool(logicalDevice, graphicsQueueFamilyIndex,
		deviceDeletionQueue);

	make_drawing_instruction_pipeline();

	currentTime = glfwGetTime();
	lastTime = currentTime;
	numFrames = 0;
	frameTime = 0.0f;
}

void Engine::make_drawing_instruction_pipeline() {

	Logger* logger = Logger::get_logger();

	//Build a frame for each instruction stage
	for (uint32_t i = 0; i < 4; ++i) {
		frames.push_back(Frame(dldi, logicalDevice, deviceDeletionQueue,
			allocate_command_buffer(logicalDevice, commandPool), swapchain,
			shaders, graphicsQueues[i]));
	}

	// "Pre record" work for command buffers
	uint32_t i = 0;

	//Frame 0: no work needed
	logicalDevice.resetFences(frames[i].renderFinishedFence);
	i++;

	//Frame 1: should have finished presenting,
	// and be aquiring a swapchain image
	frames[i].acquire_image();
	i++;

	//Frame 2: should have finished presenting,
	// aquired a swapchain image,
	// and recorded draw commands
	frames[i].acquire_image();
	frames[i].record_draw_commands();
	i++;

	//Frame 3: should have finished presenting,
	// aquired a swapchain image,
	// recorded draw commands, 
	// and be currently rendering
	frames[i].acquire_image();
	frames[i].record_draw_commands();
	frames[i].render();
	i++;

	logger->print("recorded initial state for pipeline");

	drawingJobs[0].emplace(

		[&]() {
			frames[0].acquire_image();
		},
		[&]() {
			frames[1].record_draw_commands();
		},
		[&]() {
			frames[2].render();
		},
		[&]() {
			frames[3].present();
		});

	drawingJobs[1].emplace(
		[&]() {
			frames[3].acquire_image();
		},
		[&]() {
			frames[0].record_draw_commands();
		},
		[&]() {
			frames[1].render();
		},
		[&]() {
			frames[2].present();
		});

	drawingJobs[2].emplace(
		[&]() {
			frames[2].acquire_image();
		},
		[&]() {
			frames[3].record_draw_commands();
		},
		[&]() {
			frames[0].render();
		},
		[&]() {
			frames[1].present();
		});

	drawingJobs[3].emplace(
		[&]() {
			frames[1].acquire_image();
		},
		[&]() {
			frames[2].record_draw_commands();
		},
		[&]() {
			frames[3].render();
		},
		[&]() {
			frames[0].present();
		});
}

void Engine::draw() {

	executor.run(drawingJobs[currentFrame]).wait();
	currentFrame = (currentFrame + 1) % 4;
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

	graphicsQueues[0].waitIdle();
	graphicsQueues[1].waitIdle();
	graphicsQueues[2].waitIdle();
	graphicsQueues[3].waitIdle();

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