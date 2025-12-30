#pragma once
#include <glm/glm.hpp>
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include <vector>
#include <vma/vk_mem_alloc.h>
#include <deque>
#include <functional>
#include "../renderer/buffer.h"

struct Vertex {
	alignas(16) glm::vec3 pos;
	alignas(16) glm::vec3 color;

	static vk::VertexInputBindingDescription2EXT getBindingDescription() {

		vk::VertexInputBindingDescription2EXT description = {};
		description.binding = 0;
		description.stride = sizeof(Vertex);
		description.inputRate = vk::VertexInputRate::eVertex;
		description.divisor = 1;
		return description;
	}

	static std::vector<vk::VertexInputAttributeDescription2EXT> getAttributeDescriptions() {
		std::vector<vk::VertexInputAttributeDescription2EXT> attributes(2);

		attributes[0].binding = 0;
		attributes[0].location = 0;
		attributes[0].format = vk::Format::eR32G32Sfloat;
		attributes[0].offset = offsetof(Vertex, pos);

		attributes[1].binding = 0;
		attributes[1].location = 1;
		attributes[1].format = vk::Format::eR32G32B32Sfloat;
		attributes[1].offset = offsetof(Vertex, color);

		return attributes;
	}
};

/**
* @brief Build a triangle
* 
* @param allocator The Vulkan memory allocator object.
* 
* @param vmaDeletionQueue deletion queue to hold destructor.
*/
StorageBuffer build_triangle(VmaAllocator& allocator, 
	std::deque<std::function<void(VmaAllocator)>>& vmaDeletionQueue,
	vk::CommandBuffer commandBuffer, vk::Queue queue);