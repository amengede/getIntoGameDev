#pragma once
#include "../config.h"
#include "vkUtil/frame.h"
#include "vkImage/image.h"
#include "../model/scene.h"

class Engine {

public:

	Engine(int width, int height, GLFWwindow* window);

	~Engine();

	void render(Scene* scene);

private:

	bool multithreaded = true;

	//glfw-related variables
	int width;
	int height;
	GLFWwindow* window;

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
	vk::Pipeline pipeline;

	//descriptor-related variables
	vk::DescriptorSetLayout frameSetLayout;
	vk::DescriptorPool frameDescriptorPool;

	//Command-related variables
	vk::CommandPool commandPool;
	vk::CommandBuffer mainCommandBuffer;

	//Synchronization objects
	int maxFramesInFlight, frameNumber;

	//instance setup
	void make_instance();

	//device setup
	void make_device();
	void make_swapchain();
	void recreate_swapchain();

	//pipeline setup
	void make_descriptor_set_layouts();
	void make_pipelines();

	//final setup steps
	void finalize_setup();
	void make_frame_resources();

	void prepare_frame(uint32_t imageIndex, Scene* scene);
	void prepare_to_raycast_barrier(vk::CommandBuffer commandBuffer, vk::Image image);
	void dispatch_raycast(vk::CommandBuffer commandBuffer, uint32_t imageIndex);
	void prepare_to_present_barrier(vk::CommandBuffer commandBuffer, vk::Image image);

	//Cleanup functions
	void cleanup_swapchain();
};