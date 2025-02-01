#pragma once
#include "../../config.h"
#include "../vkUtil/queue_families.h"

/*
* Vulkan separates the concept of physical and logical devices. 
* 
  A physical device usually represents a single complete implementation of Vulkan 
  (excluding instance-level functionality) available to the host, 
  of which there are a finite number. 
  
  A logical device represents an instance of that implementation 
  with its own state and resources independent of other logical devices.
*/

namespace vkInit {

	/**
		Check whether the physical device can support the given extensions.

		\param device the physical device to check
		\param requestedExtensions a list of extension names to check against
		\returns whether all of the extensions are requested
	*/
	bool checkDeviceExtensionSupport(
		const vk::PhysicalDevice& device,
		const std::vector<const char*>& requestedExtensions
	) {

		/*
		* Check if a given physical device can satisfy a list of requested device
		* extensions.
		*/

		std::set<std::string> requiredExtensions(requestedExtensions.begin(), requestedExtensions.end());

		vkLogging::Logger::get_logger()->print("Device can support extensions:");

		for (vk::ExtensionProperties& extension : device.enumerateDeviceExtensionProperties()) {

			if (vkLogging::Logger::get_logger()->get_debug_mode()) {
				std::cout << "\t\"" << extension.extensionName << "\"\n";
			}

			//remove this from the list of required extensions (set checks for equality automatically)
			requiredExtensions.erase(extension.extensionName);
		}

		//if the set is empty then all requirements have been satisfied
		return requiredExtensions.empty();
	}

	/**
		Check whether the given physical device is suitable for use.

		\param device the physical device
		\returns whether the device is suitable
	*/
	bool isSuitable(const vk::PhysicalDevice& device) {

		vkLogging::Logger::get_logger()->print("Checking if device is suitable");

		/*
		* A device is suitable if it can present to the screen, ie support
		* the swapchain extension
		*/
		const std::vector<const char*> requestedExtensions = {
			VK_KHR_SWAPCHAIN_EXTENSION_NAME
		};

		vkLogging::Logger::get_logger()->print("We are requesting device extensions:");
		if (vkLogging::Logger::get_logger()->get_debug_mode()) {

			for (const char* extension : requestedExtensions) {
				std::cout << "\t\"" << extension << "\"\n";
			}

		}

		if (checkDeviceExtensionSupport(device, requestedExtensions)) {
			vkLogging::Logger::get_logger()->print("Device can support the requested extensions!");
		}
		else {
			vkLogging::Logger::get_logger()->print("Device can't support the requested extensions!");
			return false;
		}
		return true;
	}

	/**
		Choose a physical device for the vulkan instance.

		\param instance the vulkan instance to use
		\returns the chosen physical device
	*/
	vk::PhysicalDevice choose_physical_device(const vk::Instance& instance) {

		/*
		* Choose a suitable physical device from a list of candidates.
		* Note: Physical devices are neither created nor destroyed, they exist
		* independently to the program.
		*/

		vkLogging::Logger::get_logger()->print("Choosing Physical Device");

		/*
		* ResultValueType<std::vector<PhysicalDevice, PhysicalDeviceAllocator>>::type
			Instance::enumeratePhysicalDevices( Dispatch const & d )

		  std::vector<vk::PhysicalDevice> instance.enumeratePhysicalDevices( Dispatch const & d = static/default )
		*/
		std::vector<vk::PhysicalDevice> availableDevices = instance.enumeratePhysicalDevices();

		std::stringstream message;
		message << "There are " << availableDevices.size() << " physical devices available on this system";
		vkLogging::Logger::get_logger()->print(message.str());

		/*
		* check if a suitable device can be found
		*/
		for (vk::PhysicalDevice device : availableDevices) {

			if (vkLogging::Logger::get_logger()->get_debug_mode()) {
				vkLogging::log_device_properties(device);
			}
			if (isSuitable(device)) {
				return device;
			}
		}

		return nullptr;
	}

	/**
		Create a Vulkan device

		\param physicalDevice the Physical Device to represent
		\param surface the window surface
		\returns the created device
	*/
	vk::Device create_logical_device(vk::PhysicalDevice physicalDevice, vk::SurfaceKHR surface) {

		/*
		* Create an abstraction around the GPU
		*/

		/*
		* At time of creation, any required queues will also be created,
		* so queue create info must be passed in.
		*/

		vkUtil::QueueFamilyIndices indices = vkUtil::findQueueFamilies(physicalDevice, surface);
		std::vector<uint32_t> uniqueIndices;
		uniqueIndices.push_back(indices.graphicsFamily.value());
		if (indices.graphicsFamily.value() != indices.presentFamily.value()) {
			uniqueIndices.push_back(indices.presentFamily.value());
		}
		/*
		* VULKAN_HPP_CONSTEXPR DeviceQueueCreateInfo( VULKAN_HPP_NAMESPACE::DeviceQueueCreateFlags flags_            = {},
                                                uint32_t                                     queueFamilyIndex_ = {},
                                                uint32_t                                     queueCount_       = {},
                                                const float * pQueuePriorities_ = {} ) VULKAN_HPP_NOEXCEPT
		*/
		std::vector<vk::DeviceQueueCreateInfo> queueCreateInfo;
		float queuePriority = 1.0f;
		for (uint32_t queueFamilyIndex : uniqueIndices) {
			queueCreateInfo.push_back(
				vk::DeviceQueueCreateInfo(
					vk::DeviceQueueCreateFlags(), queueFamilyIndex, 1, &queuePriority
				)
			);
		}

		/*
		* Device features must be requested before the device is abstracted,
		* therefore we only pay for what we need.
		*/

		vk::PhysicalDeviceFeatures deviceFeatures = vk::PhysicalDeviceFeatures();

		/*
		* Device extensions to be requested:
		*/
		std::vector<const char*> deviceExtensions = {
			VK_KHR_SWAPCHAIN_EXTENSION_NAME
		};

		/*
		* VULKAN_HPP_CONSTEXPR DeviceCreateInfo( VULKAN_HPP_NAMESPACE::DeviceCreateFlags flags_                         = {},
                                           uint32_t                                queueCreateInfoCount_          = {},
                                           const VULKAN_HPP_NAMESPACE::DeviceQueueCreateInfo * pQueueCreateInfos_ = {},
                                           uint32_t                                            enabledLayerCount_ = {},
                                           const char * const * ppEnabledLayerNames_                              = {},
                                           uint32_t             enabledExtensionCount_                            = {},
                                           const char * const * ppEnabledExtensionNames_                          = {},
                                           const VULKAN_HPP_NAMESPACE::PhysicalDeviceFeatures * pEnabledFeatures_ = {} )
		*/
		std::vector<const char*> enabledLayers;
		if (vkLogging::Logger::get_logger()->get_debug_mode()) {
			enabledLayers.push_back("VK_LAYER_KHRONOS_validation");
		}
		vk::DeviceCreateInfo deviceInfo = vk::DeviceCreateInfo(
			vk::DeviceCreateFlags(), 
			static_cast<uint32_t>(queueCreateInfo.size()), queueCreateInfo.data(),
			static_cast<uint32_t>(enabledLayers.size()), enabledLayers.data(),
			static_cast<uint32_t>(deviceExtensions.size()), deviceExtensions.data(),
			&deviceFeatures
		);

		try {
			vk::Device device = physicalDevice.createDevice(deviceInfo);
			vkLogging::Logger::get_logger()->print("GPU has been successfully abstracted!");
			return device;
		}
		catch (vk::SystemError err) {
			vkLogging::Logger::get_logger()->print("Device creation failed!");
			return nullptr;
		}
		return nullptr;
	}

	/**
		Get the queues associated with the physical device.

		\param physicalDevice the physical device
		\param device the logical device
		\param surface the window surface
		\returns the queues
	*/
	std::array<vk::Queue,2> get_queues(vk::PhysicalDevice physicalDevice, vk::Device device, vk::SurfaceKHR surface) {

		vkUtil::QueueFamilyIndices indices = vkUtil::findQueueFamilies(physicalDevice, surface);

		return { {
				device.getQueue(indices.graphicsFamily.value(), 0),
				device.getQueue(indices.presentFamily.value(), 0),
			} };
	}

}