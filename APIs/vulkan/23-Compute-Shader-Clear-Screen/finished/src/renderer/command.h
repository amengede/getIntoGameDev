#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include <deque>
#include <functional>
#include "../logging/logger.h"

/**
* @brief Make a command pool!
* 
* @param logicalDevice the vulkan device
* @param queueFamilyIndex the index of the Queue Family on which
*	command buffers from this pool will be submitted.
* @param deletionQueue deletion queue
* 
* @returns the new command pool
*/
vk::CommandPool make_command_pool(vk::Device logicalDevice, uint32_t queueFamilyIndex,
	std::deque<std::function<void(vk::Device)>>& deletionQueue);

/**
* @brief allocate a command buffer.
* 
* @param logicalDevice the vulkan device
* @param commandPool the command pool to allocate from
* 
* @returns the allocated command buffer
*/
vk::CommandBuffer allocate_command_buffer(vk::Device logicalDevice, vk::CommandPool commandPool);