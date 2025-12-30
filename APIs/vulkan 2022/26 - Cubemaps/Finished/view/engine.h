#pragma once
#include "../config.h"
#include "vkUtil/frame.h"
#include "../model/scene.h"
#include "../model/vertex_menagerie.h"
#include "vkImage/texture.h"
#include "vkImage/cubemap.h"

class Engine {

public:

	Engine(int width, int height, GLFWwindow* window);

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
	std::vector<pipelineType> pipelineTypes = { {pipelineType::SKY, pipelineType::STANDARD} };
	std::unordered_map<pipelineType,vk::PipelineLayout> pipelineLayout;
	std::unordered_map < pipelineType, vk::RenderPass> renderpass;
	std::unordered_map < pipelineType, vk::Pipeline> pipeline;

	//descriptor-related variables
	std::unordered_map < pipelineType, vk::DescriptorSetLayout> frameSetLayout;
	vk::DescriptorPool frameDescriptorPool; //Descriptors bound on a "per frame" basis
	std::unordered_map < pipelineType, vk::DescriptorSetLayout> meshSetLayout;
	vk::DescriptorPool meshDescriptorPool; //Descriptors bound on a "per mesh" basis

	//Command-related variables
	vk::CommandPool commandPool;
	vk::CommandBuffer mainCommandBuffer;

	//Synchronization objects
	int maxFramesInFlight, frameNumber;

	//asset pointers
	VertexMenagerie* meshes;
	std::unordered_map<meshTypes, vkImage::Texture*> materials;
	vkImage::CubeMap* cubemap;

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
	void make_framebuffers();
	void make_frame_resources();

	//asset creation
	void make_assets();

	void prepare_frame(uint32_t imageIndex, Scene* scene);
	void prepare_scene(vk::CommandBuffer commandBuffer);
	void record_draw_commands_sky(vk::CommandBuffer commandBuffer, uint32_t imageIndex, Scene* scene);
	void record_draw_commands_scene(vk::CommandBuffer commandBuffer, uint32_t imageIndex, Scene* scene);
	void render_objects(
		vk::CommandBuffer commandBuffer, meshTypes objectType, uint32_t& startInstance, uint32_t instanceCount);

	//Cleanup functions
	void cleanup_swapchain();
};