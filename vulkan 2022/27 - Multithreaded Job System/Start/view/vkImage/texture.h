#pragma once
#include "../../config.h"
#include "image.h"

namespace vkImage {

	class Texture {

	public:

		Texture(TextureInputChunk input);

		void use(vk::CommandBuffer commandBuffer, vk::PipelineLayout pipelineLayout);

		~Texture();

	private:

		int width, height, channels;
		vk::Device logicalDevice;
		vk::PhysicalDevice physicalDevice;
		const char* filename;
		stbi_uc* pixels;

		//Resources
		vk::Image image;
		vk::DeviceMemory imageMemory;
		vk::ImageView imageView;
		vk::Sampler sampler;

		//Resource Descriptors
		vk::DescriptorSetLayout layout;
		vk::DescriptorSet descriptorSet;
		vk::DescriptorPool descriptorPool;

		vk::CommandBuffer commandBuffer;
		vk::Queue queue;

		/**
			Load the raw image data from the internally set filepath.
		*/
		void load();

		/**
			Send loaded data to the image. The image must be loaded before calling
			this function.
		*/
		void populate();

		/**
			Create a view of the texture. The image must be populated before calling this function.
		*/
		void make_view();

		/**
			Configure and create a sampler for the texture.
		*/
		void make_sampler();

		/**
			Allocate and write the descriptor set. Currently, this is only being done once.
			This must be called after the image view and sampler have been made.
		*/
		void make_descriptor_set();
	};
}