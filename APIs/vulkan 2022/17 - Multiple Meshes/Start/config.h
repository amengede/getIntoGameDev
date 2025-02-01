#pragma once
#include <vulkan/vulkan.hpp>

#include <GLFW/glfw3.h>

#include <iostream>
#include <vector>
#include <set>
#include <string>
#include <optional>
#include <fstream>
#include <sstream>

#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

/**
	Data structures used for creating buffers
	and allocating memory
*/
struct BufferInputChunk {
	size_t size;
	vk::BufferUsageFlagBits usage;
	vk::Device logicalDevice;
	vk::PhysicalDevice physicalDevice;
};

/**
	holds a vulkan buffer and memory allocation
*/
struct Buffer {
	vk::Buffer buffer;
	vk::DeviceMemory bufferMemory;
};