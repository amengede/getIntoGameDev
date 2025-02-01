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