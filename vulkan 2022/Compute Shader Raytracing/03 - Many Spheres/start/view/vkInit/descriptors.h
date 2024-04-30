#pragma once
#include "../../config.h"

namespace vkInit {

	/**
		Describes the bindings of a descriptor set layout
	*/
	struct descriptorSetLayoutData {
		int count;
		std::vector<int> indices;
		std::vector<vk::DescriptorType> types;
		std::vector<int> counts;
		std::vector<vk::ShaderStageFlags> stages;
	};

	/**
		Make a descriptor set layout from the given descriptions

		\param device the logical device
		\param bindings	a struct describing the bindings used in the shader
		\returns the created descriptor set layout
	*/
	vk::DescriptorSetLayout make_descriptor_set_layout(
		vk::Device device, const descriptorSetLayoutData& bindings);

	/**
		Make a descriptor pool

		\param device the logical device
		\param size the number of descriptor sets to allocate from the pool
		\param bindings	used to get the descriptor types
		\returns the created descriptor pool
	*/
	vk::DescriptorPool make_descriptor_pool(
		vk::Device device, uint32_t size, const descriptorSetLayoutData& bindings);

	/**
		Allocate a descriptor set from a pool.

		\param device the logical device
		\param descriptorPool the pool to allocate from
		\param layout the descriptor set layout which the set must adhere to
		\returns the allocated descriptor set
	*/
	vk::DescriptorSet allocate_descriptor_set(
		vk::Device device, vk::DescriptorPool descriptorPool,
		vk::DescriptorSetLayout layout);
}