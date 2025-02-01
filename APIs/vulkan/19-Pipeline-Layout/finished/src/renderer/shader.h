#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include <deque>
#include <functional>

/**
* @brief builds pipeline layouts
*/
class PipelineLayoutBuilder {
public:

	/**
	* @param logicalDevice the Vulkan device used to build pipeline layouts
	*/
	PipelineLayoutBuilder(vk::Device& logicalDevice);

	/**
	* @brief build a pipeline layout with the current state, then reset state
	* 
	* @param deletionQueue the deletion queue
	*/
	vk::PipelineLayout build(std::deque<std::function<void(vk::Device)>>& deletionQueue);

	/**
	* @brief add a descriptor set layout to the current state
	*/
	void add(vk::DescriptorSetLayout descriptorSetLayout);
private:

	/**
	* @brief the Vulkan device used to build pipeline layouts
	*/
	vk::Device& logicalDevice;

	/**
	* @brief the collection of descriptor set layouts used in the pipeline
	*/
	std::vector<vk::DescriptorSetLayout> descriptorSetLayouts;

	/**
	* @brief reset the current state
	*/
	void reset();
};

/**
 * @brief Create a shader object
 * 
 * @param logicalDevice vulkan device
 * @param name shader name, shader files are in the "shaders" folder, 
 *      with the extensions .vert and .frag
 * @param filename name of the file holding the code
 * @return vk::ShaderEXT The created shader object
 */
std::vector<vk::ShaderEXT> make_shader_objects(vk::Device logicalDevice,
    const char* name,
    vk::DispatchLoaderDynamic& dl, 
    std::deque<std::function<void(vk::Device)>>& deviceDeletionQueue);