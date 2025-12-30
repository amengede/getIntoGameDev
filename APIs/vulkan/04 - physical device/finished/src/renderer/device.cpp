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