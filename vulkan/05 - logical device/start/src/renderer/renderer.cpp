#include "renderer.h"
#include "device.h"

Engine::Engine(GLFWwindow* window) :
	window(window) {

	logger = Logger::get_logger();
	logger->print("Made a graphics engine");

	instance = make_instance("Real Engine", instanceDeletionQueue);
	dldi = vk::DispatchLoaderDynamic(instance, vkGetInstanceProcAddr);
	debugMessenger = logger->make_debug_messenger(instance, dldi, instanceDeletionQueue);
	logger->set_mode(false);

	physicalDevice = choose_physical_device(instance);

	logger->set_mode(true);
	logicalDevice = create_logical_device(physicalDevice, deviceDeletionQueue);
	uint32_t graphicsQueueFamilyIndex = findQueueFamilyIndex(
		physicalDevice, vk::QueueFlagBits::eGraphics);
	graphicsQueue = logicalDevice.getQueue(graphicsQueueFamilyIndex, 0);
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