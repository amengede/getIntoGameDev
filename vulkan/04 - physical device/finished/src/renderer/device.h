#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>

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