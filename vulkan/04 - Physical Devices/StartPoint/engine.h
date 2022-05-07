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

	//debug callback
	vk::DebugUtilsMessengerEXT debugMessenger{ nullptr };

	//dynamic instance dispatcher
	vk::DispatchLoaderDynamic dldi;

	//glfw setup
	void build_glfw_window();

	//instance setup
	void make_instance();

	//debug messenger
	void make_debug_messenger();
};