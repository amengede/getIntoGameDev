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
	uint32_t requestedExtensionCount = 3;
	const char** ppRequestedExtensions = (const char**)malloc(requestedExtensionCount * sizeof(char*));
	ppRequestedExtensions[0] = "VK_KHR_swapchain";
	ppRequestedExtensions[1] = "VK_EXT_shader_object";
	ppRequestedExtensions[2] = "VK_KHR_dynamic_rendering";

	if (supports(device, ppRequestedExtensions, requestedExtensionCount)) {
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
	vk::PhysicalDevice bestDevice = nullptr;
	bool foundDiscrete = false;

	for (vk::PhysicalDevice device : availableDevices) {

		logger->log(device);

		vk::PhysicalDeviceProperties properties = device.getProperties();

		if (is_suitable(device)) {

			// Prefer discrete GPU if possible
			bool discrete = properties.deviceType == vk::PhysicalDeviceType::eDiscreteGpu;
			if (!foundDiscrete) {
				bestDevice = device;
			}
			else if (discrete) {
				foundDiscrete = true;
				bestDevice = device;
			}
		}
	}

	return bestDevice;
}

uint32_t find_queue_family_index(vk::PhysicalDevice physicalDevice,
	vk::SurfaceKHR surface,
    vk::QueueFlags queueType) {
	
	Logger* logger = Logger::get_logger();

	std::vector<vk::QueueFamilyProperties> queueFamilies = physicalDevice.getQueueFamilyProperties();
	logger->log(queueFamilies);

	for (uint32_t i = 0; i < queueFamilies.size(); ++i) {
		vk::QueueFamilyProperties queueFamily = queueFamilies[i];

		bool canPresent = false;
		if (surface) {
			if (physicalDevice.getSurfaceSupportKHR(i, surface)
					.result == vk::Result::eSuccess) {
				canPresent = true;
			}
		}
		else {
			canPresent = true;
		}

		bool supported = false;
		if (queueFamily.queueFlags & queueType) {
			supported = true;
		}

		if (supported && canPresent) {
			return i;
		}
	}
	return UINT32_MAX;
}

vk::Device create_logical_device(
    vk::PhysicalDevice physicalDevice,
	vk::SurfaceKHR surface,
    std::deque<std::function<void(vk::Device)>>& deletionQueue) {
	
	Logger* logger = Logger::get_logger();

	uint32_t graphicsIndex = find_queue_family_index(physicalDevice, surface, vk::QueueFlagBits::eGraphics);
	float queuePriority = 1.0f;
	vk::DeviceQueueCreateInfo queueInfo = vk::DeviceQueueCreateInfo(
		vk::DeviceQueueCreateFlags(), graphicsIndex, 1, &queuePriority
	);

	//Request features
	vk::PhysicalDeviceFeatures deviceFeatures = vk::PhysicalDeviceFeatures();
	vk::PhysicalDeviceShaderObjectFeaturesEXT shaderFeatures = vk::PhysicalDeviceShaderObjectFeaturesEXT(1);
	vk::PhysicalDeviceVulkan13Features vulkan13Features;
	vulkan13Features.setSynchronization2(true);
	vulkan13Features.setDynamicRendering(true);

	//Chain them together
	shaderFeatures.pNext = &vulkan13Features;

	uint32_t enabled_layer_count = 1;
	const char** ppEnabledLayers = nullptr;
	if (logger->is_enabled()) {
		enabled_layer_count = 1;
		ppEnabledLayers = (const char**) malloc(sizeof(const char*));
		ppEnabledLayers[0] = "VK_LAYER_KHRONOS_validation";
	}

	uint32_t enabledExtensionCount = 3;
	const char** ppEnabledExtensions = (const char**) malloc(enabledExtensionCount * sizeof(char*));
	ppEnabledExtensions[0] = "VK_KHR_swapchain";
	ppEnabledExtensions[1] = "VK_EXT_shader_object";
	ppEnabledExtensions[2] = "VK_KHR_dynamic_rendering";

	vk::DeviceCreateInfo deviceInfo = vk::DeviceCreateInfo(
		vk::DeviceCreateFlags(),
		1, &queueInfo,
		enabled_layer_count, ppEnabledLayers,
		enabledExtensionCount, ppEnabledExtensions,
		&deviceFeatures);
	deviceInfo.pNext = &shaderFeatures;
	
	vk::ResultValueType<vk::Device>::type logicalDevice = physicalDevice.createDevice(deviceInfo);
	vk::Device device = nullptr;
	if (logicalDevice.result == vk::Result::eSuccess) {
		logger->print("GPU has been successfully abstracted!");

		deletionQueue.push_back([logger](vk::Device device) {
			device.destroy();
			logger->print("Deleted logical device");
		});

		device = logicalDevice.value;
	}
	else {
		logger->print("Device creation failed!");
	}

	if (ppEnabledLayers) {
		free(ppEnabledLayers);
	}
	free(ppEnabledExtensions);
	return device;
}