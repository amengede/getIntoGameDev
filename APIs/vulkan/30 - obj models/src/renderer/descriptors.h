/*---------------------------------------------------------------------------*/
/*	Descriptor utility functions
/*---------------------------------------------------------------------------*/
#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include "device.h"
#include "../backend/dynamic_array.h"

/**
* @brief Binding scopes for descriptors
*/
enum class DescriptorScope {
	eFrame,
	eDrawCall,
	ePost,
};

/**
* @brief Builds descriptor sets
*/
class DescriptorSetLayoutBuilder {
public:

	/**
	* @brief Construct a descriptor set layout builder
	* 
	* @param logicalDevice the vulkan device to build with.
	*/
	DescriptorSetLayoutBuilder(Device& device);

	/**
	* @brief build a descriptor set layout using current state, 
	* then reset state
	* 
	* @param deletionQueue the deletion queue for the descriptor set layout
	*/
	vk::DescriptorSetLayout build();

	/**
	* @brief Add a descriptor set entry. This function assumes there will 
	* only be one descriptor of that type.
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
	Device& device;

	/**
	* @brief the bindings in the set layout
	*/
	DynamicArray<vk::DescriptorSetLayoutBinding> layoutBindings;

	/**
	* @brief reset the layoutBindings to start building a new set layout
	*/
	void reset();
};

/**
* @brief Make a descriptor pool
*
* @param device the logical device
* @param descriptorSetCount the number of descriptor sets to allocate 
* from the pool
* @param bindingCount the number of descriptors to be bound in the set
* @param pBindingTypes the type of each binding
* @param deletionQueue deletion queue
* 
* @returns the created descriptor pool
*/
vk::DescriptorPool make_descriptor_pool(
	Device device, uint32_t descriptorSetCount,
	DynamicArray<vk::DescriptorType> bindingTypes);

/**
* @brief Allocate a descriptor set from a pool.
*
* @param device the logical device
* @param descriptorPool the pool to allocate from
* @param layout the descriptor set layout which the set must adhere to
* 
* @returns the allocated descriptor set
*/
vk::DescriptorSet allocate_descriptor_set(
	vk::Device device, vk::DescriptorPool descriptorPool,
	vk::DescriptorSetLayout layout);
/*---------------------------------------------------------------------------*/