#pragma once
#include "../../config.h"

namespace vkUtil {

	/**
		Holds the indices of the graphics and presentation queue families.
	*/
	struct QueueFamilyIndices {
		std::optional<uint32_t> graphicsFamily;
		std::optional<uint32_t> presentFamily;

		bool isComplete() {
			return graphicsFamily.has_value() && presentFamily.has_value();
		}
	};

	/**
		Find suitable queue family indices on the given physical device.

		\param device the physical device to check
		\param surface the window surface
		\returns a struct holding the queue family indices
	*/
	QueueFamilyIndices findQueueFamilies(vk::PhysicalDevice device, vk::SurfaceKHR surface) {
		QueueFamilyIndices indices;

		std::vector<vk::QueueFamilyProperties> queueFamilies = device.getQueueFamilyProperties();

		std::stringstream message;
		message << "There are " << queueFamilies.size() << " queue families available on the system.";
		vkLogging::Logger::get_logger()->print(message.str());
		message.str("");

		int i = 0;
		for (vk::QueueFamilyProperties queueFamily : queueFamilies) {

			/*
			* // Provided by VK_VERSION_1_0
				typedef struct VkQueueFamilyProperties {
				VkQueueFlags    queueFlags;
				uint32_t        queueCount;
				uint32_t        timestampValidBits;
				VkExtent3D      minImageTransferGranularity;
				} VkQueueFamilyProperties;

				queueFlags is a bitmask of VkQueueFlagBits indicating capabilities of the queues in this queue family.

				queueCount is the unsigned integer count of queues in this queue family. Each queue family must support
				at least one queue.

				timestampValidBits is the unsigned integer count of meaningful bits in the timestamps written via
				vkCmdWriteTimestamp. The valid range for the count is 36..64 bits, or a value of 0,
				indicating no support for timestamps. Bits outside the valid range are guaranteed to be zeros.

				minImageTransferGranularity is the minimum granularity supported for image transfer
				operations on the queues in this queue family.
			*/

			/*
			* // Provided by VK_VERSION_1_0
				typedef enum VkQueueFlagBits {
				VK_QUEUE_GRAPHICS_BIT = 0x00000001,
				VK_QUEUE_COMPUTE_BIT = 0x00000002,
				VK_QUEUE_TRANSFER_BIT = 0x00000004,
				VK_QUEUE_SPARSE_BINDING_BIT = 0x00000008,
				} VkQueueFlagBits;
			*/

			if (queueFamily.queueFlags & vk::QueueFlagBits::eGraphics) {
				indices.graphicsFamily = i;

				message << "Queue Family " << i << " is suitable for graphics.";
				vkLogging::Logger::get_logger()->print(message.str());
				message.str("");
			}

			if (device.getSurfaceSupportKHR(i, surface)) {
				indices.presentFamily = i;

				message << "Queue Family " << i << " is suitable for presenting.";
				vkLogging::Logger::get_logger()->print(message.str());
				message.str("");
			}

			if (indices.isComplete()) {
				break;
			}

			i++;
		}

		return indices;
	}
}