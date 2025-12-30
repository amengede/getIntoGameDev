#include "memory.h"
#include "../logging/logger.h"
#include <sstream>
#include <string>

VmaPool mem::create_pool(const ImagePoolCreateInfo& imagePoolInfo) {

	Logger* logger = Logger::get_logger();

	// Example image
	VkImageCreateInfo exampleImage = { VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO };
	exampleImage.usage = imagePoolInfo.usage;
	exampleImage.samples = VK_SAMPLE_COUNT_1_BIT;

	// Example allocation
	VmaAllocationCreateInfo exampleAllocation = {};
	exampleAllocation.usage = VMA_MEMORY_USAGE_AUTO;
	if (imagePoolInfo.hostWrite) {
		exampleAllocation.flags = VMA_ALLOCATION_CREATE_HOST_ACCESS_SEQUENTIAL_WRITE_BIT;
	}

	uint32_t memoryTypeIndex;
	VkResult result = vmaFindMemoryTypeIndexForImageInfo(
		imagePoolInfo.allocator, &exampleImage, 
		&exampleAllocation, &memoryTypeIndex);

	std::stringstream messageBuilder;
	messageBuilder << "Memory type index: " << memoryTypeIndex;
	std::string message = messageBuilder.str();
	logger->print(message);

	VmaPoolCreateInfo poolInfo = {};
	poolInfo.memoryTypeIndex = memoryTypeIndex;
	if (imagePoolInfo.freeAtOnce) {
		poolInfo.flags |= VMA_POOL_CREATE_LINEAR_ALGORITHM_BIT;
	}
	poolInfo.minAllocationAlignment = imagePoolInfo.alignment;
	poolInfo.minBlockCount = imagePoolInfo.blockCount;
	poolInfo.maxBlockCount = imagePoolInfo.blockCount;
	poolInfo.pMemoryAllocateNext = nullptr;

	VmaPool pool;
	result = vmaCreatePool(imagePoolInfo.allocator, &poolInfo, &pool);

	return pool;
}