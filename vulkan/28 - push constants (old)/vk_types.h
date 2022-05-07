#pragma once
#include <vulkan/vulkan.h>

struct Buffer {
	VkBuffer buffer;
	VkDeviceMemory memory;
};

struct Image {
	VkImage image;
	VkDeviceMemory memory;
	VkImageView view;
	uint32_t mipLevels = 1;
};