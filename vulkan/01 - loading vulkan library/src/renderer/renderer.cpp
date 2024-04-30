#include "renderer.h"

Engine::Engine(GLFWwindow* window) :
	window(window) {

	logger = Logger::get_logger();
	logger->print("Made a graphics engine");
}

Engine::~Engine() {

	logger->print("Goodbye see you!");
}