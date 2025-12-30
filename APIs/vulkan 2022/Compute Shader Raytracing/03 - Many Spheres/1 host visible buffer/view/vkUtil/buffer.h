#pragma once
#include "../../config.h"

class Buffer {
public:
	vk::Buffer buffer;
	vk::DeviceMemory deviceMemory;
	size_t size;
	vk::DescriptorBufferInfo descriptor;

	void create_resources(vk::Device logicalDevice);

	void blit(void* data, size_t _size);

	void destroy(vk::Device logicalDevice);

private:
	void* writeLocation;
};