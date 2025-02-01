#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include <deque>
#include <functional>

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