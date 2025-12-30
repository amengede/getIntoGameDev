#include "memory.h"
#include "single_time_commands.h"

uint32_t vkUtil::findMemoryTypeIndex(vk::PhysicalDevice physicalDevice, uint32_t supportedMemoryIndices, vk::MemoryPropertyFlags requestedProperties) {

	/*
	* // Provided by VK_VERSION_1_0
	typedef struct VkPhysicalDeviceMemoryProperties {
		uint32_t        memoryTypeCount;
		VkMemoryType    memoryTypes[VK_MAX_MEMORY_TYPES];
		uint32_t        memoryHeapCount;
		VkMemoryHeap    memoryHeaps[VK_MAX_MEMORY_HEAPS];
	} VkPhysicalDeviceMemoryProperties;
	*/
	vk::PhysicalDeviceMemoryProperties memoryProperties = physicalDevice.getMemoryProperties();

	for (uint32_t i = 0; i < memoryProperties.memoryTypeCount; i++) {

		//bit i of supportedMemoryIndices is set if that memory type is supported by the device
		bool supported{ static_cast<bool>(supportedMemoryIndices & (1 << i)) };

		//propertyFlags holds all the memory properties supported by this memory type
		bool sufficient{ (memoryProperties.memoryTypes[i].propertyFlags & requestedProperties) == requestedProperties };

		if (supported && sufficient) {
			return i;
		}
	}

	return 0;
}

void vkUtil::allocateBufferMemory(Buffer& buffer, const BufferInputChunk& input) {

	/*
	// Provided by VK_VERSION_1_0
	typedef struct VkMemoryRequirements {
		VkDeviceSize    size;
		VkDeviceSize    alignment;
		uint32_t        memoryTypeBits;
	} VkMemoryRequirements;
	*/
	vk::MemoryRequirements memoryRequirements = input.logicalDevice.getBufferMemoryRequirements(buffer.buffer);

	/*
	* // Provided by VK_VERSION_1_0
	typedef struct VkMemoryAllocateInfo {
		VkStructureType    sType;
		const void*        pNext;
		VkDeviceSize       allocationSize;
		uint32_t           memoryTypeIndex;
	} VkMemoryAllocateInfo;
	*/
	vk::MemoryAllocateInfo allocInfo;
	allocInfo.allocationSize = memoryRequirements.size;
	allocInfo.memoryTypeIndex = findMemoryTypeIndex(
		input.physicalDevice, memoryRequirements.memoryTypeBits,
		input.memoryProperties
	);

	buffer.bufferMemory = input.logicalDevice.allocateMemory(allocInfo);
	input.logicalDevice.bindBufferMemory(buffer.buffer, buffer.bufferMemory, 0);
}

vkUtil::Buffer vkUtil::createBuffer(BufferInputChunk input) {

	/*
	* // Provided by VK_VERSION_1_0
	typedef struct VkBufferCreateInfo {
		VkStructureType        sType;
		const void*            pNext;
		VkBufferCreateFlags    flags;
		VkDeviceSize           size;
		VkBufferUsageFlags     usage;
		VkSharingMode          sharingMode;
		uint32_t               queueFamilyIndexCount;
		const uint32_t*        pQueueFamilyIndices;
	} VkBufferCreateInfo;
	*/
	vk::BufferCreateInfo bufferInfo;
	bufferInfo.flags = vk::BufferCreateFlags();
	bufferInfo.size = input.size;
	bufferInfo.usage = input.usage;
	bufferInfo.sharingMode = vk::SharingMode::eExclusive;

	Buffer buffer;
	buffer.buffer = input.logicalDevice.createBuffer(bufferInfo);

	allocateBufferMemory(buffer, input);
	return buffer;
}

void vkUtil::copyBuffer(Buffer& srcBuffer, Buffer& dstBuffer, vk::DeviceSize size, vk::Queue queue, vk::CommandBuffer commandBuffer) {

	vkUtil::startJob(commandBuffer);

	/*
	* // Provided by VK_VERSION_1_0
	typedef struct VkBufferCopy {
		VkDeviceSize    srcOffset;
		VkDeviceSize    dstOffset;
		VkDeviceSize    size;
	} VkBufferCopy;
	*/
	vk::BufferCopy copyRegion;
	copyRegion.srcOffset = 0;
	copyRegion.dstOffset = 0;
	copyRegion.size = size;
	commandBuffer.copyBuffer(srcBuffer.buffer, dstBuffer.buffer, 1, &copyRegion);

	vkUtil::endJob(commandBuffer, queue);
}