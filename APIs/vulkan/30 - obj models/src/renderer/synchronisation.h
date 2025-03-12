/*---------------------------------------------------------------------------*/
/*  Synchronization objects
/*---------------------------------------------------------------------------*/
#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include "device.h"

/**
 * @brief Create a semaphore
 *
 * @param logicalDevice vulkan device
 * @return the new semaphore
 */
vk::Semaphore make_semaphore(Device& logicalDevice);

/**
 * @brief Create a fence
 *
 * @param logicalDevice vulkan device
 * @param deviceDeletionQueue Deletion queue
 * @return the new fence
 */
vk::Fence make_fence(Device& logicalDevice);
/*---------------------------------------------------------------------------*/