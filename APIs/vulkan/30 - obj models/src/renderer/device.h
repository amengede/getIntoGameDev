/*---------------------------------------------------------------------------*/
/*  Logical and Physical Device functions
/*---------------------------------------------------------------------------*/
#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include <deque>
#include <functional>

struct Device {

	vk::Device device = nullptr;
	std::deque<std::function<void(vk::Device)>> deletionQueue;

	void free() {
		flush_deletion_queue();
		device.destroy();
	}

	void flush_deletion_queue() {

		while (deletionQueue.size() > 0) {
			deletionQueue.back()(device);
			deletionQueue.pop_back();
		}
	}
};

/**
 * @brief Chooses a physical device for use
 * 
 * @param instance Vulkan instance which will use the device.
 * 
 * @returns vk::PhysicalDevice the selected physical device.
 */
vk::PhysicalDevice choose_physical_device(
    const vk::Instance& instance);

/**
 * @brief Query the given physical device for the index of
 *  a queue family.
 * 
 * @param physicalDevice Physical device to query.
 * @param surface Surface to present to, nullptr if
 *      presentation is not needed.
 * @param queueType Type of queue being queried.
 * 
 * @returns the index of the queue family, 
 *  UINT32_MAX upon failure.
 */
uint32_t find_queue_family_index(vk::PhysicalDevice physicalDevice, 
    vk::SurfaceKHR surface,
    vk::QueueFlags queueType);

/**
 * @brief Create a logical device object
 * 
 * @param physicalDevice Physical device to be abstracted
 * @param surface Surface to present to
 * @param deletionQueue holds deletion functions
 * 
 * @returns An abstraction of the physical device
 */
vk::Device create_logical_device(
    vk::PhysicalDevice physicalDevice,
    vk::SurfaceKHR surface,
    std::deque<std::function<void(vk::Device)>>& deletionQueue);
/*---------------------------------------------------------------------------*/