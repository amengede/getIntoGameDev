#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include <deque>
#include <functional>

/**
* @brief Create a Vulkan instance.
*
* @param applicationName the name of the application.
* @param deletionQueue Queue onto which to push the instance's destructor.
* 
* @return the instance created.
*/
vk::Instance make_instance(const char* applicationName, std::deque<std::function<void()>>& deletionQueue);