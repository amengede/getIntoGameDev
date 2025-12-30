/*---------------------------------------------------------------------------*/
/*	Image utility functions
/*---------------------------------------------------------------------------*/
#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include "../backend/memory.h"
#include "device.h"

/**
* @brief Storage Image!
*/
class StorageImage {

public:

	/**
	* @brief Make a new storage image
	* 
	* @param allocator memory allocator object
	* @param format image format
	* @param extent image size
	* @param commandBuffer command buffer (for initial image transition)
	* @param queue GPU Queue
	* @param logicalDevice Vulkan device
	* @param name the image name (useful for debug purposes)
	*/
	StorageImage(mem::Allocator& allocator,
		vk::Format format,
		vk::Extent2D extent,
		vk::CommandBuffer commandBuffer,
		vk::Queue queue, Device logicalDevice,
		const char* name);

	/**
	* @brief Resource descriptor
	*/
	vk::DescriptorImageInfo descriptor;

	/**
	* @brief Image size
	*/
	vk::Extent2D extent;

	/**
	* @brief vulkan image
	*/
	vk::Image image;

	/**
	* @brief underlying memory
	*/
	VmaAllocation memory;

	/**
	* @brief Image view (handle for GPU to use)
	*/
	vk::ImageView view;

	/**
	* @brief Image format
	*/
	vk::Format format;

private:

	/**
	* @brief Do all the internal jobs to initialize the image
	* 
	* @param commandBuffer Vulkan command buffer
	* @param queue GPU work queue
	* @param logicalDevice Vulkan device
	*/
	void initialize(vk::CommandBuffer commandBuffer, vk::Queue queue,
		vk::Device logicalDevice);

	/**
	* @brief make a view of the image
	* 
	* @param logicalDevice Vulkan device
	*/
	void make_view(vk::Device logicalDevice);

	/**
	* @brief Make a descriptor for the resource
	*/
	void make_descriptor();
};

/**
	For making individual vulkan images
*/
struct ImageInputChunk {
	vk::Extent2D extent;
	vk::ImageTiling tiling = vk::ImageTiling::eLinear;
	vk::ImageUsageFlags usage;
	vk::MemoryPropertyFlags memoryProperties;
	vk::Format format = vk::Format::eR8G8B8A8Unorm;
	vk::ImageCreateFlags flags;
	const char* name = nullptr;
};

/**
* @brief Make a Vulkan Image
* 
* @param allocator Vulkan Allocator object
* @param input holds all the image parameters
* @param image to be populated with the created image
* @param memory to be populated with the allocated memory
*/
void make_image(mem::Allocator& allocator, ImageInputChunk input,
	vk::Image& image, VmaAllocation& memory);

/**
 * @brief Create a image view object
 * 
 * @param logicalDevice the vulkan device
 * @param image image to view
 * @param format image format
 * 
 * @returns vk::ImageView the created image view
 */
vk::ImageView create_image_view(vk::Device logicalDevice, 
    vk::Image image, vk::Format format);

/**
* @brief Record an image layout transition onto a command buffer
* 
* @param commandBuffer command buffer to record to
* @param image the image whose layout to transition
* @param oldLayout the old layout
* @param newLayout the new layout
* @param srcAccessMask the operation after which to start transition
* @param dstAccessMask the operation which will wait on the transition
* @param srcStage the pipeline stage after which to start transition
* @param dstStage the pipeline stage which will wait on the transition
*/
void transition_image_layout(vk::CommandBuffer commandBuffer, vk::Image image,
    vk::ImageLayout oldLayout, vk::ImageLayout newLayout, 
    vk::AccessFlags srcAccessMask, vk::AccessFlags dstAccessMask,
    vk::PipelineStageFlags srcStage, vk::PipelineStageFlags dstStage);

/**
* @brief copy from one image to another.
* 
* @param commandBuffer command buffer
* @param src Image to copy from
* @param dst Image to copy to
* @param srcSize size of the source image
* @param dstSize size of the destination image
*/
void copy_image_to_image(vk::CommandBuffer commandBuffer,
	vk::Image src, vk::Image dst, vk::Extent2D srcSize, vk::Extent2D dstSize);
/*---------------------------------------------------------------------------*/