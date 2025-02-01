#include "buffer.h"
#include "memory.h"

Buffer::Buffer(vk::Device logicalDevice, vk::PhysicalDevice physicalDevice, size_t size, vk::BufferUsageFlags usage) {

	//Make Staging Buffer
	vkUtil::BufferInputChunk input;
	input.logicalDevice = logicalDevice;
	input.memoryProperties = vk::MemoryPropertyFlagBits::eHostVisible | vk::MemoryPropertyFlagBits::eHostCoherent;
	input.physicalDevice = physicalDevice;
	input.size = size;
	input.usage = vk::BufferUsageFlagBits::eTransferSrc;
	vkUtil::BufferOutputChunk  chunk = vkUtil::createBuffer(input);
	stagingBuffer = chunk.buffer;
	stagingMemory = chunk.memory;
	stagingSize = chunk.size;

	//Make Device Buffer
	input.memoryProperties = vk::MemoryPropertyFlagBits::eDeviceLocal;
	input.usage = usage | vk::BufferUsageFlagBits::eTransferDst;
	chunk = vkUtil::createBuffer(input);
	buffer = chunk.buffer;
	deviceMemory = chunk.memory;
	size = chunk.size;

	create_resources(logicalDevice);
}

void Buffer::create_resources(vk::Device logicalDevice) {

	writeLocation = logicalDevice.mapMemory(stagingMemory, 0, stagingSize);

	descriptor.buffer = buffer;
	descriptor.offset = 0;
	descriptor.range = stagingSize;

}

void Buffer::blit(void* data, size_t _size, vk::Queue queue, vk::CommandBuffer commandBuffer) {

	memcpy(writeLocation, data, _size);

	vkUtil::copyBuffer(
		stagingBuffer, buffer, _size,
		queue, commandBuffer
	);

}

void Buffer::destroy(vk::Device logicalDevice) {

	logicalDevice.unmapMemory(stagingMemory);
	logicalDevice.freeMemory(stagingMemory);
	logicalDevice.destroyBuffer(stagingBuffer);

	logicalDevice.freeMemory(deviceMemory);
	logicalDevice.destroyBuffer(buffer);

}