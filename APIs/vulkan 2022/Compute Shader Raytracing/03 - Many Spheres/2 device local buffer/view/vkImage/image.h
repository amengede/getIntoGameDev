#pragma once
#include "../../config.h"

namespace vkImage {

	/**
		For making the Image class
	*/
	struct TextureInputChunk {
		vk::Device logicalDevice;
		vk::PhysicalDevice physicalDevice;
		std::vector<const char*> filenames;
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
		vk::Format format;
		uint32_t arrayCount;
		vk::ImageCreateFlags flags;
	};

	/**
		For transitioning image layouts
	*/
	struct ImageLayoutTransitionJob {
		vk::CommandBuffer commandBuffer;
		vk::Queue queue;
		vk::Image image;
		vk::ImageLayout oldLayout, newLayout;
		uint32_t arrayCount;
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
		uint32_t arrayCount;
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
	vk::ImageView make_image_view(
		vk::Device logicalDevice, vk::Image image, vk::Format format,
		vk::ImageAspectFlags aspect, vk::ImageViewType type, uint32_t arrayCount);

	/**
		\returns an image format supporting the requested tiling and features
	*/
	vk::Format find_supported_format(
		vk::PhysicalDevice physicalDevice,
		const std::vector<vk::Format>& candidates, 
		vk::ImageTiling tiling, vk::FormatFeatureFlags features);
}