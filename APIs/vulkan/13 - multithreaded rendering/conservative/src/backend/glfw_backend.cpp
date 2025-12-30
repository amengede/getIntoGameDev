#include "glfw_backend.h"
#include "../logging/logger.h"
#include <sstream>

GLFWwindow* build_window(int width, int height, const char* name) {

	Logger* logger = Logger::get_logger();

	glfwInit();

	//no default rendering client, we'll hook vulkan up
	//to the window later
	glfwWindowHint(GLFW_CLIENT_API, GLFW_NO_API);
	//resizing breaks the swapchain, we'll disable it for now
	glfwWindowHint(GLFW_RESIZABLE, GLFW_FALSE);

	//GLFWwindow* glfwCreateWindow (int width, int height, const char *title, GLFWmonitor *monitor, GLFWwindow *share)
	GLFWwindow* window = glfwCreateWindow(width, height, name, nullptr, nullptr);
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