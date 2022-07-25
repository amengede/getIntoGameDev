#pragma once
#include "config.h"
#include "frame.h"

class Engine {

public:

	Engine();

	~Engine();

private:

	//whether to print debug messages in functions
	bool debugMode = true;

	//glfw-related variables
	int width{ 640 };
	int height{ 480 };
	GLFWwindow* window{ nullptr };

	//instance-related variables
	vk::Instance instance{ nullptr };
	vk::DebugUtilsMessengerEXT debugMessenger{ nullptr };
	vk::DispatchLoaderDynamic dldi;
	vk::SurfaceKHR surface;

	//device-related variables
	vk::PhysicalDevice physicalDevice{ nullptr };
	vk::Device device{ nullptr };
	vk::Queue graphicsQueue{ nullptr };
	vk::Queue presentQueue{ nullptr };
	vk::SwapchainKHR swapchain{ nullptr };
	std::vector<vkUtil::SwapChainFrame> swapchainFrames;
	vk::Format swapchainFormat;
	vk::Extent2D swapchainExtent;

	//pipeline-related variables
	vk::PipelineLayout pipelineLayout;
	vk::RenderPass renderpass;
	vk::Pipeline pipeline;


	//glfw setup
	void build_glfw_window();

	//instance setup
	void make_instance();

	//device setup
	void make_device();

	//pipeline setup
	void make_pipeline();
};