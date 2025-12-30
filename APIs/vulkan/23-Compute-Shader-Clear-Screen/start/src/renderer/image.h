#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include <vma/vk_mem_alloc.h>
#include <deque>
#include <functional>

/**
* @brief Storage Image!
*/
class StorageImage {

public:

	/**
	* @brief Make a new storage image
	* 
	* @param allocator memory allocator object
	* @param extent image size
	* @param commandBuffer command buffer (for initial image transition)
	* @param queue GPU Queue
	* @param logicalDevice Vulkan device
	* @param vmaDeletionQueue allocator deletion queue
	* @param deviceDeletionQueue device deletion queue
	*/
	StorageImage(VmaAllocator& allocator,
		vk::Extent2D extent,
		vk::CommandBuffer commandBuffer,
		vk::Queue queue, vk::Device logicalDevice,
		std::deque<std::function<void(VmaAllocator)>>& vmaDeletionQueue,
		std::deque<std::function<void(vk::Device)>>& deviceDeletionQueue);

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
	vk::ImageTiling tiling;
	vk::ImageUsageFlags usage;
	vk::MemoryPropertyFlags memoryProperties;
	vk::Format format;
	vk::ImageCreateFlags flags;
};

/**
* @brief Make a Vulkan Image
* 
* @param allocator Vulkan Allocator object
* @param input holds all the image parameters
* @param image to be populated with the created image
* @param memory to be populated with the allocated memory
*/
void make_image(VmaAllocator& allocator, ImageInputChunk input,
	vk::Image& image, VmaAllocation& memory);

/**
 * @brief Create a image view object
 * 
 * @param logicalDevice the vulkan device
 * @param image image to view
 * @param format image format
 * @return vk::ImageView the created image view
 */
vk::ImageView create_image_view(vk::Device logicalDevice, 
    vk::Image image, vk::Format format);

/**
* @brief Record an image layout transition onto a command buffer
* 
* @param commandBuffer to record to
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