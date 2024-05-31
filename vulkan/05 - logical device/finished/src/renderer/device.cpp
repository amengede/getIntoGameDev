#include "device.h"
#include "../logging/logger.h"

bool supports(
    const vk::PhysicalDevice& device,
	const char** ppRequestedExtensions,
	const uint32_t requestedExtensionCount) {
    
    Logger* logger = Logger::get_logger();
    logger->print("Requested Physical Device Extensions:");
    logger->print_list(ppRequestedExtensions, requestedExtensionCount);

    std::vector<vk::ExtensionProperties> extensions = device.enumerateDeviceExtensionProperties().value;
    logger->print("Physical Device Supported Extensions:");
    logger->print_extensions(extensions);

    for (uint32_t i = 0; i < requestedExtensionCount; ++i) {
        bool supported = false;

	for (vk::ExtensionProperties& extension : extensions) {
        std::string name = extension.extensionName;
		if (!name.compare(ppRequestedExtensions[i])) {
            supported = true;
            break;
        }
    }
        if (!supported) {
            return false;
        }
    }

    return true;
}

bool is_suitable(const vk::PhysicalDevice& device) {

	Logger* logger = Logger::get_logger();
	logger->print("Checking if device is suitable");

	/*
	* A device is suitable if it can present to the screen, ie support
	* the swapchain extension
	*/
	const char* ppRequestedExtension = VK_KHR_SWAPCHAIN_EXTENSION_NAME;

	if (supports(device, &ppRequestedExtension, 1)) {
		logger->print("Device can support the requested extensions!");
	}
	else {
		logger->print("Device can't support the requested extensions!");
		return false;
	}
	return true;
}

vk::PhysicalDevice choose_physical_device(const vk::Instance& instance) {

	Logger* logger = Logger::get_logger();
	logger->print("Choosing physical device...");

	/*
	* ResultValueType<std::vector<PhysicalDevice, PhysicalDeviceAllocator>>::type
		Instance::enumeratePhysicalDevices( Dispatch const & d )

		std::vector<vk::PhysicalDevice> instance.enumeratePhysicalDevices( Dispatch const & d = static/default )
	*/
	std::vector<vk::PhysicalDevice> availableDevices = instance.enumeratePhysicalDevices().value;

	for (vk::PhysicalDevice device : availableDevices) {

		logger->log(device);
		if (is_suitable(device)) {
			return device;
		}
	}

	return nullptr;
}

uint32_t findQueueFamilyIndex(vk::PhysicalDevice physicalDevice, 
    vk::QueueFlags queueType) {

	Logger* logger = Logger::get_logger();
	
	std::vector<vk::QueueFamilyProperties> queueFamilies = physicalDevice.getQueueFamilyProperties();

	logger->log(queueFamilies);

	for (uint32_t i = 0; i < queueFamilies.size(); ++i) {

		vk::QueueFamilyProperties queueFamily = queueFamilies[i];

		if (queueFamily.queueFlags & queueType) {
			return i;
		}
	}

	return UINT32_MAX;
}

vk::Device create_logical_device(vk::PhysicalDevice physicalDevice, 
	std::deque<std::function<void(vk::Device)>>& deletionQueue) {
	Logger* logger = Logger::get_logger();

	/*
	* At time of creation, any required queues will also be created,
	* so queue create info must be passed in.
	*/
	uint32_t graphicsIndex = findQueueFamilyIndex(
		physicalDevice, vk::QueueFlagBits::eGraphics);
	float queuePriority = 1.0f;
	/*
	* VULKAN_HPP_CONSTEXPR DeviceQueueCreateInfo(
		VULKAN_HPP_NAMESPACE::DeviceQueueCreateFlags flags_	= {},
        uint32_t                          queueFamilyIndex_ = {},
        uint32_t                          queueCount_       = {},
        const float * pQueuePriorities_ = {} ) VULKAN_HPP_NOEXCEPT
	*/
	vk::DeviceQueueCreateInfo queueCreateInfo = vk::DeviceQueueCreateInfo(
		vk::DeviceQueueCreateFlags(), graphicsIndex, 
		1, &queuePriority);

	/*
	* Device features must be requested before the device is abstracted,
	* so that we only pay for what we need.
	*/
	vk::PhysicalDeviceFeatures deviceFeatures = vk::PhysicalDeviceFeatures();

	/*
	* VULKAN_HPP_CONSTEXPR DeviceCreateInfo(
		VULKAN_HPP_NAMESPACE::DeviceCreateFlags flags_	= {},
        uint32_t         queueCreateInfoCount_          = {},
        const VULKAN_HPP_NAMESPACE::DeviceQueueCreateInfo * pQueueCreateInfos_ = {},
        uint32_t                     enabledLayerCount_ = {},
        const char * const * ppEnabledLayerNames_       = {},
        uint32_t             enabledExtensionCount_     = {},
        const char * const * ppEnabledExtensionNames_   = {},
        const VULKAN_HPP_NAMESPACE::PhysicalDeviceFeatures * pEnabledFeatures_ = {} )
	*/
	uint32_t enabledLayerCount = 0;
	const char** ppEnabledLayers = nullptr;
	if (logger->is_enabled()) {
		enabledLayerCount = 1;
		ppEnabledLayers = (const char**)malloc(sizeof(const char*));
		ppEnabledLayers[0] = "VK_LAYER_KHRONOS_validation";
	}

	/*
	* Extensions
	*/
	uint32_t enabledExtensionCount = 1;
	const char** ppEnabledExtensions = (const char**)malloc(enabledExtensionCount * sizeof(char*));

	uint32_t offset = 0;
	ppEnabledExtensions[offset++] = "VK_KHR_portability_subset";

	vk::DeviceCreateInfo deviceInfo = vk::DeviceCreateInfo(
		vk::DeviceCreateFlags(), 
		1, &queueCreateInfo,
		enabledLayerCount, ppEnabledLayers,
		enabledExtensionCount, ppEnabledExtensions,
		&deviceFeatures);

	
	vk::ResultValueType<vk::Device>::type logicalDevice = 
		physicalDevice.createDevice(deviceInfo);
	if (logicalDevice.result == vk::Result::eSuccess) {
		logger->print("GPU has been successfully abstracted!");

		deletionQueue.push_back([logger](vk::Device device) {
			device.destroy();
			logger->print("Deleted Logical Device!");
		});

		return logicalDevice.value;
	}
	else {
		logger->print("Device creation failed!");
		return nullptr;
	}
}