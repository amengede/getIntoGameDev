/*---------------------------------------------------------------------------*/
/*	Shader & Pipeline stuff
/*---------------------------------------------------------------------------*/
#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include "device.h"
#include "../backend/dynamic_array.h"

/**
* @brief Pipeline types
*/
enum class PipelineType {
	eClear,
	eRasterizeSmall,
	eRasterizeBig,
	eWriteColor,
};

/**
* @brief builds pipeline layouts
*/
class PipelineLayoutBuilder {
public:

	/**
	* @param logicalDevice the Vulkan device used to build pipeline layouts
	*/
	PipelineLayoutBuilder(Device& device);

	/**
	* @brief build a pipeline layout with the current state, then reset state
	*/
	vk::PipelineLayout build();

	/**
	* @brief add a descriptor set layout to the current state
	*/
	void add(vk::DescriptorSetLayout descriptorSetLayout);
private:

	/**
	* @brief the Vulkan device used to build pipeline layouts
	*/
	Device& device;

	/**
	* @brief the collection of descriptor set layouts used in the pipeline
	*/
	DynamicArray<vk::DescriptorSetLayout> descriptorSetLayouts;

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
DynamicArray<vk::ShaderEXT> make_shader_objects(vk::Device logicalDevice,
    const char* name,
    vk::detail::DispatchLoaderDynamic& dl, 
    std::deque<std::function<void(vk::Device)>>& deviceDeletionQueue);

/**
 * @brief Create a compute shader
 *
 * @param device vulkan device
 * @param name shader name, shader files are in the "shaders" folder
 * @param dl Dynamic loader (used to fetch the shader object functions)
 * @param setLayouts descriptor set layouts to use in the shader
 * 
 * @return vk::ShaderEXT The created shader object
 */
vk::ShaderEXT make_compute_shader(Device device,
	const char* name,
	vk::detail::DispatchLoaderDynamic& dl,
	DynamicArray<vk::DescriptorSetLayout>& setLayouts);
/*---------------------------------------------------------------------------*/
