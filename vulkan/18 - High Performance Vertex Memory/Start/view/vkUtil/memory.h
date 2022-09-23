#pragma once
#include "../../config.h"

namespace vkUtil {

	uint32_t findMemoryTypeIndex(
		vk::PhysicalDevice physicalDevice, uint32_t supportedMemoryIndices, 
		vk::MemoryPropertyFlags requestedProperties);

	void allocateBufferMemory(Buffer& buffer, const BufferInputChunk& input);

	Buffer createBuffer(BufferInputChunk input);
}