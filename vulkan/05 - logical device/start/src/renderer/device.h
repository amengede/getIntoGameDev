#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include <deque>
#include <functional>

/**
 * @brief Checks whether the physical device can support
 * the requested extensions
 * 
 * @param device physical device to check.
 * @param ppRequestedExtensions requested extension names
 * @param requestedExtensionCount number of requested extensions
 * @return true if all are supported
 * @return false otherwise
 */
bool supports(
    const vk::PhysicalDevice& device,
	const char** ppRequestedExtensions,
	const uint32_t requestedExtensionCount);

/**
 * @brief Checks whether the given device is suitable
 * 
 * @param device Physical device to check
 * @return true Physical device is suitable
 * @return false Physical device is unsuitable
 */
bool is_suitable(const vk::PhysicalDevice& device);

/**
 * @brief Chooses a physical device for use
 * 
 * @param instance Vulkan instance which will use the device.
 * @return vk::PhysicalDevice the selected physical device.
 */
vk::PhysicalDevice choose_physical_device(
    const vk::Instance& instance);

/**
 * @brief Query the given physical device for the index of
 *  a queue family.
 * 
 * @param physicalDevice Physical device to query.
 * @param queueType Type of queue being queried.
 * @return uint32_t the index of the queue family, 
 *  max upon failure.
 */
uint32_t findQueueFamilyIndex(vk::PhysicalDevice physicalDevice, 
    vk::QueueFlags queueType);

/**
 * @brief Create a logical device object
 * 
 * @param physicalDevice Physical device to be abstracted
 * @param deletionQueue holds deletion functions
 * @return vk::Device An abstraction of the physical device
 */
vk::Device create_logical_device(
    vk::PhysicalDevice physicalDevice,
    std::deque<std::function<void(vk::Device)>>& deletionQueue);