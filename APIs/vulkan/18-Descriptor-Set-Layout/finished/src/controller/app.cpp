#include "app.h"

App::App(GLFWwindow* window) : window(window) {
	logger = Logger::get_logger();

	main_loop();
}

void App::main_loop() {
	while (!glfwWindowShouldClose(window)) {
		glfwPollEvents();
	}

	logger->print("Window closed.");
}