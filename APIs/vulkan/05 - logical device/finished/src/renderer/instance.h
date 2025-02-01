#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include <deque>
#include <functional>

/**
* @brief Check whether the requested extensions and layers are supported.
*
* @param extensionNames a list of extension names being requested.
* @param extensionCount the number of requested extensions.
* @param layerNames a list of layer names being requested.
* @param layerCount the number of requested layers.
*
* @return whether all of the extensions and layers are supported.
*/
bool supported_by_instance(const char** extensionNames, int extensionCount, const char** layerNames, int layerCount);

/**
* @brief Create a Vulkan instance.
*
* @param applicationName the name of the application.
* @param deletionQueue Queue onto which to push the instance's destructor.
* 
* @return the instance created.
*/
vk::Instance make_instance(const char* applicationName, std::deque<std::function<void(vk::Instance)>>& deletionQueue);