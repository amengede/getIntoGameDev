#pragma once
#include <GLFW/glfw3.h>

class Engine {

public:

	Engine();

	~Engine();

private:

	//whether to print debug messages in functions
	bool debugMode = true;

	//glfw window parameters
	int width{ 640 };
	int height{ 480 };
	GLFWwindow* window{ nullptr };

	//glfw setup
	void build_glfw_window();
};