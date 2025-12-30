#include "renderer.h"

Engine::Engine(GLFWwindow* window) :
	window(window) {

	logger = Logger::get_logger();
	logger->print("Made a graphics engine");

	instance = make_instance("Real Engine", deletionQueue);
}

Engine::~Engine() {

	logger->print("Goodbye see you!");

	while (deletionQueue.size() > 0) {
		deletionQueue.back()();
		deletionQueue.pop_back();
	}
}