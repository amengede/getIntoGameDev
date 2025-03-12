#include "device.h"
#include "../logging/logger.h"
#include "../backend/dynamic_array.h"

/**
 * @brief Checks whether the physical device can support
 * the requested extensions
 *
 * @param device physical device to check.
 * @param ppRequestedExtensions requested extension names
 * @param requestedExtensionCount number of requested extensions
 * 
 * @returns whether all extensions are supported
 */
bool supports(
    const vk::PhysicalDevice& device,
	DynamicArray<const char*> requestedExtensions) {
    
    Logger* logger = Logger::get_logger();
    logger->print("Requested Physical Device Extensions:");
    logger->print(requestedExtensions);

	DynamicArray<vk::ExtensionProperties> extensions;
	uint32_t extensionCount;
	device.enumerateDeviceExtensionProperties(NULL, &extensionCount, NULL);
	extensions.resize(extensionCount);
	device.enumerateDeviceExtensionProperties(NULL, &extensionCount, extensions.data);
    logger->print("Physical Device Supported Extensions:");
    logger->print(extensions);

    for (size_t i = 0; i < requestedExtensions.size; ++i) {
        bool supported = false;

		for (size_t j = 0; j < extensions.size; ++j) {
			vk::ExtensionProperties extension = extensions[j];
			std::string name = extension.extensionName;
			if (!name.compare(requestedExtensions[i])) {
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

/**
 * @brief Checks whether the given device is suitable
 *
 * @param device Physical device to check
 * 
 * @returns whether the Physical device is suitable
 */
bool is_suitable(const vk::PhysicalDevice& device) {

	Logger* logger = Logger::get_logger();
	logger->print("Checking if device is suitable");

	/*
	* A device is suitable if it can present to the screen, ie support
	* the swapchain extension
	*/
	DynamicArray<const char*> requestedExtensions;
	requestedExtensions.push_back("VK_KHR_swapchain");
	requestedExtensions.push_back("VK_EXT_shader_object");
	requestedExtensions.push_back("VK_KHR_dynamic_rendering");
	requestedExtensions.push_back("VK_EXT_shader_image_atomic_int64");

	if (supports(device, requestedExtensions)) {
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

	DynamicArray<vk::PhysicalDevice> availableDevices;
	uint32_t count;
	instance.enumeratePhysicalDevices(&count, NULL);
	availableDevices.resize(count);
	instance.enumeratePhysicalDevices(&count, availableDevices.data);
	vk::PhysicalDevice bestDevice = nullptr;
	bool foundDiscrete = false;

	for (size_t i = 0; i < availableDevices.size; ++i) {
		
		vk::PhysicalDevice device = availableDevices[i];
		logger->print(device);

		vk::PhysicalDeviceProperties properties = device.getProperties();

		if (is_suitable(device)) {

			// Prefer discrete GPU if possible
			bool discrete = properties.deviceType == 
							vk::PhysicalDeviceType::eDiscreteGpu;
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

	DynamicArray<vk::QueueFamilyProperties> queueFamilies;
	uint32_t queueFamilyCount;
	physicalDevice.getQueueFamilyProperties(&queueFamilyCount, NULL);
	queueFamilies.resize(queueFamilyCount);
	physicalDevice.getQueueFamilyProperties(&queueFamilyCount, queueFamilies.data);
	logger->print(queueFamilies);

	for (uint32_t i = 0; i < queueFamilies.size; ++i) {
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

	uint32_t graphicsIndex = 
		find_queue_family_index(physicalDevice, surface, vk::QueueFlagBits::eGraphics);
	float queuePriority = 1.0f;
	vk::DeviceQueueCreateInfo queueInfo = vk::DeviceQueueCreateInfo(
		vk::DeviceQueueCreateFlags(), graphicsIndex, 1, &queuePriority
	);

	//Request features
	vk::PhysicalDeviceFeatures deviceFeatures = vk::PhysicalDeviceFeatures();
	deviceFeatures.setShaderInt64(true);
	vk::PhysicalDeviceShaderObjectFeaturesEXT shaderFeatures = 
		vk::PhysicalDeviceShaderObjectFeaturesEXT(1);
	vk::PhysicalDeviceVulkan12Features vulkan12Features;
	vulkan12Features.setShaderBufferInt64Atomics(true);
	vk::PhysicalDeviceVulkan13Features vulkan13Features;
	vulkan13Features.setSynchronization2(true);
	vulkan13Features.setDynamicRendering(true);
	vk::PhysicalDeviceShaderImageAtomicInt64FeaturesEXT atomicFeatures;
	atomicFeatures.setShaderImageInt64Atomics(true);

	//Chain them together
	shaderFeatures.pNext = &vulkan12Features;
	vulkan12Features.setPNext(&vulkan13Features);
	vulkan13Features.setPNext(&atomicFeatures);

	uint32_t enabled_layer_count = 0;
	const char** ppEnabledLayers = nullptr;
	if (logger->is_enabled()) {
		enabled_layer_count = 1;
		ppEnabledLayers = (const char**) malloc(sizeof(const char*));
		ppEnabledLayers[0] = "VK_LAYER_KHRONOS_validation";
	}

	uint32_t enabledExtensionCount = 4;
	const char** ppEnabledExtensions = 
		(const char**) malloc(enabledExtensionCount * sizeof(char*));
	ppEnabledExtensions[0] = "VK_KHR_swapchain";
	ppEnabledExtensions[1] = "VK_EXT_shader_object";
	ppEnabledExtensions[2] = "VK_KHR_dynamic_rendering";
	ppEnabledExtensions[3] = "VK_EXT_shader_image_atomic_int64";

	vk::DeviceCreateInfo deviceInfo = vk::DeviceCreateInfo(
		vk::DeviceCreateFlags(),
		1, &queueInfo,
		enabled_layer_count, ppEnabledLayers,
		enabledExtensionCount, ppEnabledExtensions,
		&deviceFeatures);
	deviceInfo.pNext = &shaderFeatures;
	
	vk::ResultValueType<vk::Device>::type logicalDevice = 
		physicalDevice.createDevice(deviceInfo);
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