#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include <deque>
#include <functional>

/**
 * @brief Create a shader object
 * 
 * @param logicalDevice vulkan device
 * @param stage shader stage for the module
 * @param filename name of the file holding the code
 * @return vk::ShaderEXT The created shader object
 */
std::vector<vk::ShaderEXT> make_shader_objects(vk::Device logicalDevice,
    const char* vertexFilename, const char* fragmentFilename,
    vk::detail::DispatchLoaderDynamic& dl, 
    std::deque<std::function<void(vk::Device)>>& deviceDeletionQueue);