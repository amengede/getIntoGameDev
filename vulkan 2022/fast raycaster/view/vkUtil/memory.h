#pragma once
#include "../../config.h"
#include "buffer.h"

namespace vkUtil {

	/**
		Data structures used for creating buffers
		and allocating memory
	*/
	struct BufferInputChunk {
		size_t size;
		vk::BufferUsageFlags usage;
		vk::Device logicalDevice;
		vk::PhysicalDevice physicalDevice;
		vk::MemoryPropertyFlags memoryProperties;
	};

	/**
		Find the index of a memory type on the GPU satisfying the given properties

		\param physicalDevice the physicalDevice to check
		\param supportedMemoryIndices indices of memory types supported by the device
		\param requestedProperties properties which the memory type must satisfy
		\returns the index of a suitable memory type
	*/
	uint32_t findMemoryTypeIndex(
		vk::PhysicalDevice physicalDevice, uint32_t supportedMemoryIndices,
		vk::MemoryPropertyFlags requestedProperties);

	/**
		Allocate a memory block for the given buffer.

		\param buffer the buffer to allocate memory for
		\param input holds various parameters
	*/
	void allocateBufferMemory(Buffer& buffer, const BufferInputChunk& input);

	/**
		Make a buffer.

		\param input holds various parameters
		\returns the created buffer
	*/
	Buffer createBuffer(BufferInputChunk input);

	/**
		Copy a buffer.

		\param srcBuffer the buffer to copy from
		\param dstBuffer the buffer to copy to
		\param size the size (in bytes) to copy
		\param queue on which to submit the job
		\param commandBuffer the command buffer on which to record the job
	*/
	void copyBuffer(Buffer& srcBuffer, Buffer& dstBuffer, vk::DeviceSize size, vk::Queue queue, vk::CommandBuffer commandBuffer);
}