/*---------------------------------------------------------------------------*/
/*	Buffer utility functions (BUF)
/*---------------------------------------------------------------------------*/
#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include "../backend/memory.h"

/**
* @brief Stores some stuff
*/
class Buffer {
public:
	/**
	* @brief Underlying Vulkan buffer object
	*/
	vk::Buffer buffer;
	
	/**
	* @brief memory allocation
	*/
	VmaAllocation allocation = nullptr;
	
	/**
	* @brief Resource descriptor, should the buffer be bound
	*/
	vk::DescriptorBufferInfo descriptor;

	/**
	* @brief Number of triangles
	*/
	uint32_t triangleCount = 0;
};

/**
* @brief Make a buffer.
* 
* @param allocator Vulkan Memory Allocator
* @param byteSize desired buffer size
* @param usage intended buffer usage
* @param hostWrite whether the buffer should be writeable by eg. memcpy
* @param name Buffer name (for debug purposes)
* 
* @returns the created buffer
*/
Buffer make_buffer(mem::Allocator& allocator, size_t byteSize,
	vk::BufferUsageFlags usage, bool hostWrite, const char* name);

/**
* @brief Make a depth buffer.
* 
* @param allocator Vulkan Memory Allocator
* @param deletionQueue Queue to hold destructor
* @param size render target size
*/
Buffer make_depth_buffer(mem::Allocator& allocator, vk::Extent2D size);

/**
* @brief Make a Uniform Buffer Object
* 
* @param allocator Vulkan Memory Allocator
* @param deletionQueue Queue to hold destructor
* @param byteSize UBO size
*/
Buffer make_ubo(mem::Allocator& allocator, size_t byteSize);

/**
* @brief Copy between buffers
*
* @param allocator Vulkan Memory Allocator
* @param src Buffer to copy from
* @param dst Buffer to copy to
* @param queue Queue to submit job on
* @param commandBuffer command buffer to record copy job
*/
void copy(VmaAllocator& allocator, Buffer& src, Buffer& dst,
	vk::Queue queue, vk::CommandBuffer commandBuffer);
/*---------------------------------------------------------------------------*/