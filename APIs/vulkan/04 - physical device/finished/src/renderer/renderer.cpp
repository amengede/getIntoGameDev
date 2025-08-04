#include "renderer.h"
#include "device.h"

Engine::Engine(GLFWwindow* window) :
	window(window) {

	logger = Logger::get_logger();
	logger->print("Made a graphics engine");

	instance = make_instance("Real Engine", deletionQueue);
	dldi = vk::detail::DispatchLoaderDynamic(instance, vkGetInstanceProcAddr);
	debugMessenger = logger->make_debug_messenger(instance, dldi, deletionQueue);

	physicalDevice = choose_physical_device(instance);
}

Engine::~Engine() {

	logger->print("Goodbye see you!");

	while (deletionQueue.size() > 0) {
		deletionQueue.back()(instance);
		deletionQueue.pop_back();
	}
}