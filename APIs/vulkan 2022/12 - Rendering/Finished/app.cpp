#include "app.h"

App::App(int width, int height, bool debug) {

	build_glfw_window(width, height, debug);

	graphicsEngine = new Engine(width, height, window, debug);
}

void App::build_glfw_window(int width, int height, bool debugMode) {

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

void App::run() {

	while (!glfwWindowShouldClose(window)) {
		glfwPollEvents();
		graphicsEngine->render();
		calculateFrameRate();
	}
}

void App::calculateFrameRate() {
	currentTime = glfwGetTime();
	double delta = currentTime - lastTime;

	if (delta >= 1) {
		int framerate{ std::max(1, int(numFrames / delta)) };
		std::stringstream title;
		title << "Running at " << framerate << " fps.";
		glfwSetWindowTitle(window, title.str().c_str());
		lastTime = currentTime;
		numFrames = -1;
		frameTime = float(1000.0 / framerate);
	}

	++numFrames;
}

App::~App() {
	delete graphicsEngine;
}