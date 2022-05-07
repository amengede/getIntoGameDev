#pragma once
#include "config.h"

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

	//vulkan instance
	vk::Instance instance{ nullptr };

	//glfw setup
	void build_glfw_window();

	//instance setup
	void make_instance();
};