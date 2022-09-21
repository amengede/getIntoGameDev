#pragma once
#include "config.h"
#include "frame.h"
#include "scene.h"
#include "triangle_mesh.h"

class Engine {

public:

	Engine(int width, int height, GLFWwindow* window, bool debug);

	~Engine();

	void render(Scene* scene);

private:

	//whether to print debug messages in functions
	bool debugMode = true;

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
	vk::RenderPass renderpass;
	vk::Pipeline pipeline;

	//Command-related variables
	vk::CommandPool commandPool;
	vk::CommandBuffer mainCommandBuffer;

	//Synchronization objects
	int maxFramesInFlight, frameNumber;

	//asset pointers
	TriangleMesh* triangleMesh;

	//instance setup
	void make_instance();

	//device setup
	void make_device();
	void make_swapchain();
	void recreate_swapchain();

	//pipeline setup
	void make_pipeline();

	//final setup steps
	void finalize_setup();
	void make_framebuffers();
	void make_frame_sync_objects();

	//asset creation
	void make_assets();

	void prepare_scene(vk::CommandBuffer commandBuffer);
	void record_draw_commands(vk::CommandBuffer commandBuffer, uint32_t imageIndex, Scene* scene);

	//Cleanup functions
	void cleanup_swapchain();
};