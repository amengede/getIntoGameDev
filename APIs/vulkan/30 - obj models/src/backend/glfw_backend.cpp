#include "glfw_backend.h"
#include "../logging/logger.h"
#include <sstream>

GLFWwindow* build_window(int width, int height, const char* name) {

	Logger* logger = Logger::get_logger();

	glfwInit();

	// Configure
	glfwWindowHint(GLFW_CLIENT_API, GLFW_NO_API);
	glfwWindowHint(GLFW_RESIZABLE, GLFW_TRUE);

	GLFWmonitor* monitor = nullptr;
	GLFWwindow* share = nullptr;
	GLFWwindow* window = glfwCreateWindow(width, height, name, monitor, share);

	// Report status
	if (window) {
		std::stringstream line;
		line << "Successfully made a glfw window called \"" << name
			<< "\", width: " << width
			<< ", height: " << height;
		logger->print(line.str());
	}
	else {
		logger->print("GLFW window creation failed.");
	}

	return window;
}