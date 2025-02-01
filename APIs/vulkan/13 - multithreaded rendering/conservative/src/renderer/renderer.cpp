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

	shaders = make_shader_objects(logicalDevice,
		"shader", dldi,
		deviceDeletionQueue);

	commandPool = make_command_pool(logicalDevice, graphicsQueueFamilyIndex,
		deviceDeletionQueue);

	for (uint32_t i = 0; i < 2; ++i) {
		frames.push_back(Frame(dldi, logicalDevice, deviceDeletionQueue,
			allocate_command_buffer(logicalDevice, commandPool), swapchain, 
			shaders, graphicsQueue));
	}

	populate_drawing_instruction_pipeline();
	record_pipeline_operations();

	currentTime = glfwGetTime();
	lastTime = currentTime;
	numFrames = 0;
	frameTime = 0.0f;
}

void Engine::populate_drawing_instruction_pipeline() {
	

	// "Pre record" work for command buffers
	uint32_t i = 0;

	//Frame 0: no work needed
	logicalDevice.resetFences(frames[i].renderFinishedFence);
	i++;

	//Frame 1: should have finished presenting,
	// and be aquiring a swapchain image
	frames[i].acquire_image_and_record_draw_commands();
	i++;
}

void Engine::record_pipeline_operations() {

	drawingJobs[0].clear();
	drawingJobs[0].emplace(
		// CPU Work
		[&]() {
			frames[0].acquire_image_and_record_draw_commands();
		},

		// GPU Work
		[&]() {
			frames[1].render_and_present();
		});

	drawingJobs[1].clear();
	drawingJobs[1].emplace(
		// CPU Work
		[&]() {
			frames[1].acquire_image_and_record_draw_commands();
		},

		// GPU Work
		[&]() {
			frames[0].render_and_present();
		});
}

void Engine::draw() {

	executor.run(drawingJobs[currentFrame]).wait();
	currentFrame = (currentFrame + 1) % 2;
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