#pragma once
#include "stb_image.h"
#include "../../config.h"

namespace vkImage {

	/**
		For making the Image class
	*/
	struct TextureInputChunk {
		vk::Device logicalDevice;
		vk::PhysicalDevice physicalDevice;
		const char* filename;
		vk::CommandBuffer commandBuffer;
		vk::Queue queue;
		vk::DescriptorSetLayout layout;
		vk::DescriptorPool descriptorPool;
	};

	/**
		For making individual vulkan images
	*/
	struct ImageInputChunk {
		vk::Device logicalDevice;
		vk::PhysicalDevice physicalDevice;
		int width, height;
		vk::ImageTiling tiling;
		vk::ImageUsageFlags usage;
		vk::MemoryPropertyFlags memoryProperties;
	};

	/**
		For transitioning image layouts
	*/
	struct ImageLayoutTransitionJob {
		vk::CommandBuffer commandBuffer;
		vk::Queue queue;
		vk::Image image;
		vk::ImageLayout oldLayout, newLayout;
	};

	/**
		For copying a buffer to an image
	*/
	struct BufferImageCopyJob {
		vk::CommandBuffer commandBuffer;
		vk::Queue queue;
		vk::Buffer srcBuffer;
		vk::Image dstImage;
		int width, height;
	};

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

	/**
		Make a Vulkan Image
	*/
	vk::Image make_image(ImageInputChunk input);

	/**
		Allocate and bind the backing memory for a Vulkan Image, this memory must
		be freed upon image destruction.
	*/
	vk::DeviceMemory make_image_memory(ImageInputChunk input, vk::Image image);

	/**
		Transition the layout of an image.

		Currently supports:

		undefined -> transfer_dst_optimal,
		transfer_dst_optimal -> shader_read_only_optimal,
	*/
	void transition_image_layout(ImageLayoutTransitionJob transitionJob);

	/**
		Copy from a buffer to an image. Image must be in the transfer_dst_optimal layout.
	*/
	void copy_buffer_to_image(BufferImageCopyJob copyJob);

	/**
		Create a view of a vulkan image.
	*/
	vk::ImageView make_image_view(vk::Device logicalDevice, vk::Image image, vk::Format format);
}