#pragma once
#include "../config.h"
#include "vkUtil/frame.h"
#include "../model/scene.h"
#include "vkJob/job.h"

class Engine {

public:

	Engine(int width, int height, GLFWwindow* window, Scene* scene);

	~Engine();

	void render(Scene* scene);

private:

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
	std::vector<pipelineType> pipelineTypes = { {pipelineType::RAYTRACE} };
	std::unordered_map<pipelineType,vk::PipelineLayout> pipelineLayout;
	std::unordered_map<pipelineType, vk::Pipeline> pipeline;

	//descriptor-related variables
	std::unordered_map<pipelineType, vk::DescriptorSetLayout> frameSetLayout;
	std::unordered_map<pipelineType, vk::DescriptorPool> frameDescriptorPool; //Descriptors bound on a "per frame" basis

	//Command-related variables
	vk::CommandPool commandPool;
	vk::CommandBuffer mainCommandBuffer;

	//Synchronization objects
	int maxFramesInFlight, frameNumber;

	//asset pointers

	//instance setup
	void make_instance();

	//device setup
	void make_device(Scene* scene);
	void make_swapchain(Scene* scene);
	void recreate_swapchain(Scene* scene);

	//pipeline setup
	void make_descriptor_set_layouts();
	void make_pipelines();

	//final setup steps
	void finalize_setup(Scene* scene);
	void make_frame_resources(Scene* scene);

	//asset creation
	void make_assets(Scene* scene);

	void prepare_frame(uint32_t imageIndex, Scene* scene);
	void prepare_scene(vk::CommandBuffer commandBuffer);
	void prepare_to_trace_barrier(vk::CommandBuffer commandBuffer, vk::Image image);
	void dispatch_raytrace(vk::CommandBuffer commandBuffer, uint32_t imageIndex);
	void prepare_to_present_barrier(vk::CommandBuffer commandBuffer, vk::Image image);

	//Cleanup functions
	void cleanup_swapchain();
};