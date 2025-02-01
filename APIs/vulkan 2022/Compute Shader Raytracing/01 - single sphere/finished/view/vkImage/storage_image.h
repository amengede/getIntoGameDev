#pragma once
#include "../../config.h"
#include "image.h"

namespace vkImage {

	class StorageImage {

	public:

		StorageImage(vk::PhysicalDevice physicalDevice, vk::Device logicalDevice, 
			uint32_t width, uint32_t height);

		void initialize(vk::CommandBuffer commandBuffer, vk::Queue queue);

		~StorageImage();

		//Resource Descriptors
		vk::DescriptorImageInfo writeDescriptor, readDescriptor;

		//Resources
		vk::Image image;
		vk::DeviceMemory imageMemory;
		vk::ImageView imageView;
		vk::Sampler sampler;

	private:

		int width, height;
		vk::Device logicalDevice;
		vk::PhysicalDevice physicalDevice;

		/**
			Create a view of the texture. The image must be populated before calling this function.
		*/
		void make_view();

		/**
			Configure and create a sampler for the texture.
		*/
		void make_sampler();

		/**
			Describe the resource.
		*/
		void make_descriptors();
	};
}