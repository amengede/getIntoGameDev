#include "engine.h"
#include <iostream>

Engine::Engine() {

	if (debugMode) {
		std::cout << "Making a graphics engine\n";
	}
	
	build_glfw_window();
}

void Engine::build_glfw_window() {

	//initialize glfw
	glfwInit();

	//no default rendering client, we'll hook vulkan up
	//to the window later
	glfwWindowHint(GLFW_CLIENT_API, GLFW_NO_API);
	//resizing breaks the swapchain, we'll disable it for now
	glfwWindowHint(GLFW_RESIZABLE, GLFW_FALSE);

	//GLFWwindow* glfwCreateWindow (int width, int height, const char *title, GLFWmonitor *monitor, GLFWwindow *share)
	if (window = glfwCreateWindow(width, height, "ID Tech 12", nullptr, nullptr)) {
		if (debugMode) {
			std::cout << "Successfully made a glfw window called \"ID Tech 12\", width: " << width << ", height: " << height << '\n';
		}
	}
	else {
		if (debugMode) {
			std::cout << "GLFW window creation failed\n";
		}
	}
}

Engine::~Engine() {

	if (debugMode) {
		std::cout << "Goodbye see you!\n";
	}

	//terminate glfw
	glfwTerminate();
}