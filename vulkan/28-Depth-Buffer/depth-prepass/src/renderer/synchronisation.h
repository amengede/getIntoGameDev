#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include <deque>
#include <functional>

/**
 * @brief Create a semaphore
 *
 * @param logicalDevice vulkan device
 * @param deviceDeletionQueue Deletion queue
 * @return the new semaphore
 */
vk::Semaphore make_semaphore(vk::Device& logicalDevice,
    std::deque<std::function<void(vk::Device)>>& deviceDeletionQueue);

/**
 * @brief Create a fence
 *
 * @param logicalDevice vulkan device
 * @param deviceDeletionQueue Deletion queue
 * @return the new fence
 */
vk::Fence make_fence(vk::Device& logicalDevice,
    std::deque<std::function<void(vk::Device)>>& deviceDeletionQueue);