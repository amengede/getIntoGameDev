/*---------------------------------------------------------------------------*/
/*	Command Pool and Buffer creation
/*---------------------------------------------------------------------------*/
#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include "../logging/logger.h"
#include "device.h"

/**
* @brief Make a command pool!
* 
* @param device the vulkan device
* @param queueFamilyIndex the index of the Queue Family on which
*	command buffers from this pool will be submitted.
* 
* @returns the new command pool
*/
vk::CommandPool make_command_pool(Device device,
	uint32_t queueFamilyIndex);

/**
* @brief allocate a command buffer.
* 
* @param logicalDevice the vulkan device
* @param commandPool the command pool to allocate from
* 
* @returns the allocated command buffer
*/
vk::CommandBuffer allocate_command_buffer(vk::Device logicalDevice,
	vk::CommandPool commandPool);
/*---------------------------------------------------------------------------*/