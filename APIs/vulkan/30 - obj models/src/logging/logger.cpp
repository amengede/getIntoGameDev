#include <iostream>
#include "logger.h"

Logger* Logger::logger;

VKAPI_ATTR VkBool32 VKAPI_CALL debugCallback(
	VkDebugUtilsMessageSeverityFlagBitsEXT messageSeverity,
	VkDebugUtilsMessageTypeFlagsEXT messageType,
	const VkDebugUtilsMessengerCallbackDataEXT* pCallbackData,
	void* pUserData) {
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

void Logger::print(DynamicArray<const char*> list) {

	if (!enabled) {
		return;
	}

	for (uint32_t i = 0; i < list.size; ++i) {
		std::cout << "\t\"" << list[i] << "\"" << std::endl;
	}
}

void Logger::print(DynamicArray<vk::ExtensionProperties>& extensions) {

	if (!enabled) {
		return;
	}

	for (size_t i = 0; i < extensions.size; ++i) {
		vk::ExtensionProperties extension = extensions[i];
		std::cout << "\t\'" << extension.extensionName << "\'" << std::endl;
	}
}

void Logger::print(DynamicArray<vk::LayerProperties>& layers) {
	if (!enabled) {
		return;
	}

	for (size_t i = 0; i < layers.size; ++i) {
		vk::LayerProperties layer = layers[i];
		std::cout << "\t \'" << layer.layerName << "\'" << std::endl;
	}
}

vk::DebugUtilsMessengerEXT Logger::make_debug_messenger(
	vk::Instance& instance, 
    vk::detail::DispatchLoaderDynamic& dldi,
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
	vk::DebugUtilsMessengerCreateInfoEXT createInfo;
	createInfo.setFlags(vk::DebugUtilsMessengerCreateFlagsEXT());
	createInfo.setMessageSeverity(vk::DebugUtilsMessageSeverityFlagBitsEXT::eWarning | vk::DebugUtilsMessageSeverityFlagBitsEXT::eError);
	createInfo.setMessageType(vk::DebugUtilsMessageTypeFlagBitsEXT::eGeneral | vk::DebugUtilsMessageTypeFlagBitsEXT::eValidation | vk::DebugUtilsMessageTypeFlagBitsEXT::ePerformance);
	createInfo.setPfnUserCallback(reinterpret_cast<vk::PFN_DebugUtilsMessengerCallbackEXT>(debugCallback));

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

void Logger::print(const vk::PhysicalDevice& device) {

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

void Logger::print(const DynamicArray<vk::QueueFamilyProperties>& queueFamilies) {

	if (!enabled) {
		return;
	}

	std::cout << "There are " << queueFamilies.size 
		<< " queue families available on the system." 
		<< std::endl;
	
	for (uint32_t i = 0; i < queueFamilies.size; ++i) {

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

		vk::QueueFamilyProperties queueFamily = queueFamilies[i];

		std::cout << "Queue Family " << i << ":" << std::endl;

		std::cout << "\tSupports " 
			<< vk::to_string(queueFamily.queueFlags) << std::endl;

		std::cout << "\tFamily supports " 
			<< queueFamily.queueCount << " queues." << std::endl;
	}
}

void Logger::print(const vk::SurfaceCapabilitiesKHR& capabilities) {

	if (!enabled) {
		return;
	}

	/*
	* typedef struct VkSurfaceCapabilitiesKHR {
		uint32_t                         minImageCount;
		uint32_t                         maxImageCount;
		VkExtent2D                       currentExtent;
		VkExtent2D                       minImageExtent;
		VkExtent2D                       maxImageExtent;
		uint32_t                         maxImageArrayLayers;
		VkSurfaceTransformFlagsKHR       supportedTransforms;
		VkSurfaceTransformFlagBitsKHR    currentTransform;
		VkCompositeAlphaFlagsKHR         supportedCompositeAlpha;
		VkImageUsageFlags                supportedUsageFlags;
	} VkSurfaceCapabilitiesKHR;
	*/
	std::cout << "Swapchain can support the following surface capabilities:" << std::endl;

	std::cout << "\tminimum image count: " 
			<< capabilities.minImageCount << std::endl;
	std::cout << "\tmaximum image count: " 
			<< capabilities.maxImageCount << std::endl;

	std::cout << "\tcurrent extent:" << std::endl;
	print(capabilities.currentExtent, "\t\t");

	std::cout << "\tminimum supported extent:" << std::endl;
	print(capabilities.minImageExtent, "\t\t");

	std::cout << "\tmaximum supported extent:" << std::endl;
	print(capabilities.maxImageExtent, "\t\t");

	std::cout << "\tmaximum image array layers: " 
		<< capabilities.maxImageArrayLayers << std::endl;

	std::cout << "\tsupported transforms: " 
		<< vk::to_string(capabilities.supportedTransforms) << std::endl;

	std::cout << "\tcurrent transform: " 
		<< vk::to_string(capabilities.currentTransform) << std::endl;

	std::cout << "\tsupported alpha operations: " 
		<< vk::to_string(capabilities.supportedCompositeAlpha) << std::endl;

	std::cout << "\tsupported image usage: " 
		<< vk::to_string(capabilities.supportedUsageFlags) << std::endl;
}

void Logger::print(const vk::Extent2D& extent, const char* prefix) {
	
	if (!enabled) {
		return;
	}

	/*typedef struct VkExtent2D {
		uint32_t    width;
		uint32_t    height;
	} VkExtent2D;
	*/

	std::cout << prefix << "width: " << extent.width << std::endl;
	std::cout << prefix << "height: " << extent.height << std::endl;
}

void Logger::print(const DynamicArray<std::string>& items, const char* prefix) {

	if (!enabled) {
		return;
	}

	for (size_t i = 0; i < items.size; ++i) {
		std::cout << prefix << items[i] << std::endl;
	}
}

void Logger::print(const DynamicArray<vk::SurfaceFormatKHR>& formats) {

	if (!enabled) {
		return;
	}

	for (size_t i = 0; i < formats.size; ++i) {
		vk::SurfaceFormatKHR supportedFormat = formats[i];
		/*
		* typedef struct VkSurfaceFormatKHR {
			VkFormat           format;
			VkColorSpaceKHR    colorSpace;
		} VkSurfaceFormatKHR;
		*/

		std::cout << "supported pixel format: " 
			<< vk::to_string(supportedFormat.format) 
			<< ", supported color space: " 
			<< vk::to_string(supportedFormat.colorSpace) 
			<< std::endl;
	}
}

void Logger::print(const DynamicArray<vk::PresentModeKHR>& modes) {

	if (!enabled) {
		return;
	}

	for (size_t i = 0; i < modes.size; ++i) {
		vk::PresentModeKHR presentMode = modes[i];
		std::cout << '\t' << vk::to_string(presentMode) << std::endl;
	}
}

void Logger::print(const VmaAllocationInfo& allocationInfo) {

	if (!enabled) {
		return;
	}

	std::cout << "---- " << allocationInfo.pName << " ----" << std::endl;
	std::cout << "\tMemory type: " << allocationInfo.memoryType << std::endl;
	std::cout << "\tMemory object: " << allocationInfo.deviceMemory << std::endl;
	std::cout << "\tOffset: " << allocationInfo.offset << std::endl;
	std::cout << "\tSize: " << allocationInfo.size << std::endl;
}

void Logger::print(const vk::MemoryRequirements& memoryRequirements) {

	if (!enabled) {
		return;
	}

	std::cout << "---- Memory Requirements ----" << std::endl;
	std::cout << "\tAlignment: " << memoryRequirements.alignment << std::endl;
	std::cout << "\tType bits: " << memoryRequirements.memoryTypeBits << std::endl;
	std::cout << "\tSize: " << memoryRequirements.size << std::endl;
}