#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include <vector>
#include <deque>
#include <functional>

/**
* @brief Builds descriptor sets
*/
class DescriptorSetLayoutBuilder {
public:

	/**
	* @param logicalDevice the vulkan device to build with.
	*/
	DescriptorSetLayoutBuilder(vk::Device& logicalDevice);

	/**
	* @brief build a descriptor set layout using current state, then reset state
	* 
	* @param deletionQueue the deletion queue for the descriptor set layout
	*/
	vk::DescriptorSetLayout build(std::deque<std::function<void(vk::Device)>>& deletionQueue);

	/**
	* @brief Add a descriptor set entry. This function assumes there will only be one descriptor of that type.
	* 
	* @param stage the shader stage(s) which the descriptor will be used in
	* 
	* @param type the type of descriptor
	*/
	void add_entry(vk::ShaderStageFlags stage, vk::DescriptorType type);
private:

	/**
	* @brief the vulkan device to build with.
	*/
	vk::Device& logicalDevice;

	/**
	* @brief the bindings in the set layout
	*/
	std::vector<vk::DescriptorSetLayoutBinding> layoutBindings;

	/**
	* @brief reset the layoutBindings to start building a new set layout
	*/
	void reset();
};

/**
* @brief Make a descriptor pool
*
* @param device the logical device
* @param descriptorSetCount the number of descriptor sets to allocate from the pool
* @param bindingCount the number of descriptors to be bound in the set
* @param pBindingTypes the type of each binding
* @param deletionQueue deletion queue
* @returns the created descriptor pool
*/
vk::DescriptorPool make_descriptor_pool(
	vk::Device device, uint32_t descriptorSetCount,
	uint32_t bindingCount, vk::DescriptorType* pBindingTypes,
	std::deque<std::function<void(vk::Device)>>& deletionQueue);

/**
* @brief Allocate a descriptor set from a pool.
*
* @param device the logical device
* @param descriptorPool the pool to allocate from
* @param layout the descriptor set layout which the set must adhere to
* @returns the allocated descriptor set
*/
vk::DescriptorSet allocate_descriptor_set(
	vk::Device device, vk::DescriptorPool descriptorPool,
	vk::DescriptorSetLayout layout);