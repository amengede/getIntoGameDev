#pragma once
#include "../../config.h"
#include "../vkImage/storage_image.h"

namespace vkUtil {

	/**
		Holds the data structures associated with a "Frame"
	*/
	class SwapChainFrame {

	public:

		//For doing work
		vk::Device logicalDevice;
		vk::PhysicalDevice physicalDevice;

		//Swapchain-type stuff
		vk::Image image;
		vk::ImageView imageView;
		int width, height;

		vk::CommandBuffer commandBuffer;

		//Sync objects
		vk::Semaphore imageAvailable, renderFinished;
		vk::Fence inFlight;

		//Resources

		//Resource Descriptors
		vk::DescriptorBufferInfo cameraVectorDescriptor;
		vk::DescriptorImageInfo colorBufferDescriptor;
		std::unordered_map<pipelineType, vk::DescriptorSet> descriptorSet;

		//Write Operations
		std::vector<vk::WriteDescriptorSet> writeOps;

		SwapChainFrame(vk::PhysicalDevice physicalDevice, vk::Device logicalDevice, 
			uint32_t width, uint32_t height);

		void make_descriptor_resources();

		void record_write_operations();

		void write_descriptor_set();

		void destroy();
	};

}