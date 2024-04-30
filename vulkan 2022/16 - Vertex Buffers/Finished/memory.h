#pragma once
#include "config.h"

namespace vkUtil {

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
}