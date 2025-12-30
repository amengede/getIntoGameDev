#include "renderer.h"
#include "device.h"
#include "shader.h"
#include "command.h"

Engine::Engine(GLFWwindow* window) :
	window(window) {

	logger = Logger::get_logger();
	logger->print("Made a graphics engine");

	instance = make_instance("Real Engine", instanceDeletionQueue);
	dldi = vk::detail::DispatchLoaderDynamic(instance, vkGetInstanceProcAddr);
	debugMessenger = logger->make_debug_messenger(instance, dldi, instanceDeletionQueue);
	//logger->set_mode(false);

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
		"shaders/vertex.spv", "shaders/fragment.spv", dldi,
		deviceDeletionQueue);

	commandPool = make_command_pool(logicalDevice, graphicsQueueFamilyIndex,
		deviceDeletionQueue);

	for (uint32_t i = 0; i < images.size(); ++i) {
		frames[i].set_command_buffer(
			allocate_command_buffer(logicalDevice, commandPool), shaders, swapchain.extent, dldi);
	}
}

void Engine::draw() {

	uint32_t imageIndex{ 0 };

	vk::SubmitInfo submitInfo = {};

	submitInfo.commandBufferCount = 1;
	submitInfo.pCommandBuffers = &frames[0].commandBuffer;

	graphicsQueue.submit(submitInfo);

	graphicsQueue.waitIdle();

	vk::PresentInfoKHR presentInfo = {};

	presentInfo.swapchainCount = 1;
	presentInfo.pSwapchains = &swapchain.chain;

	presentInfo.pImageIndices = &imageIndex;

	graphicsQueue.presentKHR(presentInfo);
	graphicsQueue.waitIdle();
}

Engine::~Engine() {

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