/*---------------------------------------------------------------------------*/
/*	Functions for making meshes of various kinds
/*---------------------------------------------------------------------------*/
#pragma once
#include <glm/glm.hpp>
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include "../renderer/buffer.h"
#include "../backend/dynamic_array.h"
#include "../backend/memory.h"
#include "../math/math.h"

/**
* @brief a 3D vertex with position and color.
*/
struct Vertex {

	/**
	* @brief <x, y, z> position
	*/
	alignas(16) glm::vec3 pos;

	/**
	* @brief <r, g, b> color
	*/
	alignas(16) glm::vec3 color;

	/**
	* @returns the vulkan binding description of this vertex format.
	*/
	static vk::VertexInputBindingDescription2EXT getBindingDescription() {
		vk::VertexInputBindingDescription2EXT description = {};
		description.binding = 0;
		description.stride = sizeof(Vertex);
		description.inputRate = vk::VertexInputRate::eVertex;
		description.divisor = 1;
		return description;
	}

	/**
	* @returns vulkan descriptions for all the attributes in this
	*	vertex format.
	*/
	static DynamicArray<vk::VertexInputAttributeDescription2EXT> 
		getAttributeDescriptions() {

		DynamicArray<vk::VertexInputAttributeDescription2EXT> attributes;
		attributes.resize(2);

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
* @param commandBuffer vulkan command buffer for memory upload
* @param queue vulkan queue on which to submit the upload job
* 
* @returns a storage buffer holding the triangle
*/
Buffer build_triangle(mem::Allocator& allocator,
	vk::CommandBuffer commandBuffer, vk::Queue queue);

/**
* @brief Build OBJ model
*
* @param allocator The Vulkan memory allocator object.
* @param commandBuffer vulkan command buffer for memory upload
* @param queue vulkan queue on which to submit the upload job
* @param filename file to read
* @param preTransform Pre-Transform to apply
*
* @returns a storage buffer holding the triangle
*/
Buffer build_obj_model(mem::Allocator& allocator,
	vk::CommandBuffer commandBuffer, vk::Queue queue,
	const char* filename, const mat4& preTransform);
/*---------------------------------------------------------------------------*/