#include <iostream>
#include "logger.h"

Logger* Logger::logger;

VKAPI_ATTR VkBool32 VKAPI_CALL debugCallback(
	VkDebugUtilsMessageSeverityFlagBitsEXT messageSeverity,
	VkDebugUtilsMessageTypeFlagsEXT messageType,
	const VkDebugUtilsMessengerCallbackDataEXT* pCallbackData,
	void* pUserData
) {
	std::cerr << "validation layer: " << pCallbackData->pMessage << std::endl;

	return VK_FALSE;
}

void Logger::set_mode(bool mode) {
	enabled = mode;
}

bool Logger::is_enabled() {
	return enabled;
}

Logger* Logger::get_logger() {
	if (!logger) {
		logger = new Logger();
	}

	return logger;
}

void Logger::print(std::string message) {

	if (!enabled) {
		return;
	}

	std::cout << message << std::endl;
}

void Logger::report_version_number(uint32_t version) {
	
	if (!enabled) {
		return;
	}

	std::cout << "System can support vulkan Variant: " << vk::apiVersionVariant(version)
		<< ", Major: " << vk::apiVersionMajor(version)
		<< ", Minor: " << vk::apiVersionMinor(version)
		<< ", Patch: " << vk::apiVersionPatch(version) << std::endl;
}

void Logger::print_list(const char** list, uint32_t count) {

	if (!enabled) {
		return;
	}

	for (uint32_t i = 0; i < count; ++i) {
		std::cout << "\t\"" << list[i] << "\"" << std::endl;
	}
}

void Logger::print_extensions(std::vector<vk::ExtensionProperties>& extensions) {

	if (!enabled) {
		return;
	}

	for (vk::ExtensionProperties extension : extensions) {
		std::cout << "\t\'" << extension.extensionName << "\'" << std::endl;
	}
}

void Logger::print_layers(std::vector<vk::LayerProperties>& layers) {

	if (!enabled) {
		return;
	}

	for (vk::LayerProperties layer : layers) {
		std::cout << "\t \'" << layer.layerName << "\'" << std::endl;
	}
}

vk::DebugUtilsMessengerEXT Logger::make_debug_messenger(
	vk::Instance& instance, vk::detail::DispatchLoaderDynamic& dldi,
	std::deque<std::function<void(vk::Instance)>>& deletionQueue) {

	if (!enabled) {
		return nullptr;
	}

	/*
	* DebugUtilsMessengerCreateInfoEXT( VULKAN_HPP_NAMESPACE::DebugUtilsMessengerCreateFlagsEXT flags_           = {},
									VULKAN_HPP_NAMESPACE::DebugUtilsMessageSeverityFlagsEXT messageSeverity_ = {},
									VULKAN_HPP_NAMESPACE::DebugUtilsMessageTypeFlagsEXT     messageType_     = {},
									PFN_vkDebugUtilsMessengerCallbackEXT                    pfnUserCallback_ = {},
									void * pUserData_ = {} )
	*/

	vk::DebugUtilsMessengerCreateInfoEXT createInfo = vk::DebugUtilsMessengerCreateInfoEXT(
		vk::DebugUtilsMessengerCreateFlagsEXT(),
		vk::DebugUtilsMessageSeverityFlagBitsEXT::eVerbose | vk::DebugUtilsMessageSeverityFlagBitsEXT::eWarning | vk::DebugUtilsMessageSeverityFlagBitsEXT::eError,
		vk::DebugUtilsMessageTypeFlagBitsEXT::eGeneral | vk::DebugUtilsMessageTypeFlagBitsEXT::eValidation | vk::DebugUtilsMessageTypeFlagBitsEXT::ePerformance,
		reinterpret_cast<vk::PFN_DebugUtilsMessengerCallbackEXT>(debugCallback),
		nullptr
	);

	vk::DebugUtilsMessengerEXT messenger = instance.createDebugUtilsMessengerEXT(createInfo, nullptr, dldi);
	VkDebugUtilsMessengerEXT handle = messenger;
	deletionQueue.push_back([this, handle, dldi](vk::Instance instance) {
		instance.destroyDebugUtilsMessengerEXT(handle, nullptr, dldi);
		if (enabled) {
			std::cout << "Deleted Debug Messenger!" << std::endl;
		}
		});

	return messenger;
}

void Logger::log(const vk::PhysicalDevice& device) {

	if (!enabled) {
		return;
	}
	vk::PhysicalDeviceProperties properties = device.getProperties();

	std::cout << "Device name: " << properties.deviceName << std::endl;

	std::cout << "Device type: ";
	switch (properties.deviceType) {

	case (vk::PhysicalDeviceType::eCpu):
		std::cout << "CPU";
		break;

	case (vk::PhysicalDeviceType::eDiscreteGpu):
		std::cout << "Discrete GPU";
		break;

	case (vk::PhysicalDeviceType::eIntegratedGpu):
		std::cout << "Integrated GPU";
		break;

	case (vk::PhysicalDeviceType::eVirtualGpu):
		std::cout << "Virtual GPU";
		break;

	default:
		std::cout << "Other";
	}
	std::cout << std::endl;
}

void Logger::log(const std::vector<vk::QueueFamilyProperties>& queueFamilies) {

	if (!enabled) {
		return;
	}

	std::cout << "There are " << queueFamilies.size() 
		<< " queue families available on the system." 
		<< std::endl;
	
	for (uint32_t i = 0; i < queueFamilies.size(); ++i) {

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

		vk::QueueFamilyProperties queueFamily = queueFamilies[i];

		std::cout << "Queue Family " << i << ":" << std::endl;

		std::cout << "\tSupports ";
		if (queueFamily.queueFlags & vk::QueueFlagBits::eCompute) {
			std::cout << "compute, ";
		}
		if (queueFamily.queueFlags & vk::QueueFlagBits::eGraphics) {
			std::cout << "graphics, ";
		}
		if (queueFamily.queueFlags & vk::QueueFlagBits::eTransfer) {
			std::cout << "transfer, ";
		}
		if (queueFamily.queueFlags & vk::QueueFlagBits::eOpticalFlowNV) {
			std::cout << "nvidia optical flow, ";
		}
		if (queueFamily.queueFlags & vk::QueueFlagBits::eSparseBinding) {
			std::cout << "sparse binding, ";
		}
		if (queueFamily.queueFlags & vk::QueueFlagBits::eProtected) {
			std::cout << "protected memory, ";
		}
		if (queueFamily.queueFlags & vk::QueueFlagBits::eVideoDecodeKHR) {
			std::cout << "video decode, ";
		}
		if (queueFamily.queueFlags & vk::QueueFlagBits::eVideoEncodeKHR) {
			std::cout << "video encode, ";
		}
		std::cout << std::endl;

		std::cout << "\tFamily supports " 
			<< queueFamily.queueCount << " queues." << std::endl;
	}
}