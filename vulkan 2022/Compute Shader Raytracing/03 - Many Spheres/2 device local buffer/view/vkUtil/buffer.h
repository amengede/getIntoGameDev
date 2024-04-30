#pragma once
#include "../../config.h"

class Buffer {
public:
	vk::Buffer buffer, stagingBuffer;
	vk::DeviceMemory deviceMemory, stagingMemory;
	size_t size, stagingSize;
	vk::DescriptorBufferInfo descriptor;

	Buffer(vk::Device logicalDevice, vk::PhysicalDevice physicalDevice, size_t size, vk::BufferUsageFlags usage);

	void create_resources(vk::Device logicalDevice);

	void blit(void* data, size_t _size, vk::Queue queue, vk::CommandBuffer commandBuffer);

	void destroy(vk::Device logicalDevice);

private:
	void* writeLocation;
};