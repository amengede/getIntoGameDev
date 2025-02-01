#include "instance.h"
#include "../logging/logger.h"
#include <GLFW/glfw3.h>
#include <sstream>
#include <cstdlib>

bool supported_by_instance(const char** extensionNames, int extensionCount, const char** layerNames, int layerCount) {

	Logger* logger = Logger::get_logger();
	std::stringstream lineBuilder;

	//check extension support
	std::vector<vk::ExtensionProperties> supportedExtensions = vk::enumerateInstanceExtensionProperties().value;

	logger->print("Instance can support the following extensions:");
	logger->print_extensions(supportedExtensions);

	bool found;
	for (int i = 0; i < extensionCount; ++i) {
		const char* extension = extensionNames[i];
		found = false;
		for (vk::ExtensionProperties supportedExtension : supportedExtensions) {
			if (strcmp(extension, supportedExtension.extensionName) == 0) {
				found = true;
				lineBuilder << "Extension \"" << extension << "\" is supported!";
				logger->print(lineBuilder.str());
				lineBuilder.str("");
				break;
			}
		}
		if (!found) {
			lineBuilder << "Extension \"" << extension << "\" is not supported!";
			logger->print(lineBuilder.str());
			return false;
		}
	}

	//check layer support
	std::vector<vk::LayerProperties> supportedLayers = vk::enumerateInstanceLayerProperties().value;

	logger->print("Instance can support the following layers:");
	logger->print_layers(supportedLayers);

	for (int i = 0; i < layerCount; ++i) {
		const char* layer = layerNames[i];
		found = false;
		for (vk::LayerProperties supportedLayer : supportedLayers) {
			if (strcmp(layer, supportedLayer.layerName) == 0) {
				found = true;
				lineBuilder << "Layer \"" << layer << "\" is supported!";
				logger->print(lineBuilder.str());
				lineBuilder.str("");
				break;
			}
		}
		if (!found) {
			lineBuilder << "Layer \"" << layer << "\" is not supported!";
			logger->print(lineBuilder.str());
			return false;
		}
	}

	return true;
}

vk::Instance make_instance(const char* applicationName, std::deque<std::function<void(vk::Instance)>>& deletionQueue) {

	Logger* logger = Logger::get_logger();

	logger->print("Making an instance...");

	uint32_t version = vk::enumerateInstanceVersion().value;

	logger->report_version_number(version);

	// set the patch to 0 for best compatibility/stability)
	version &= ~(0xFFFU);

	vk::ApplicationInfo appInfo = vk::ApplicationInfo(
		applicationName,
		version,
		"Doing it the hard way",
		version,
		version
	);

	/*
	* Extensions
	*/
	uint32_t glfwExtensionCount = 0;
	const char** glfwExtensions;
	glfwExtensions = glfwGetRequiredInstanceExtensions(&glfwExtensionCount);
	uint32_t enabledExtensionCount = glfwExtensionCount;
	if (logger->is_enabled()) {
		enabledExtensionCount++;
	}
	const char** ppEnabledExtensionNames = (const char**)malloc(enabledExtensionCount * sizeof(char*));

	uint32_t offset = 0;
	for (;offset < glfwExtensionCount; ++offset) {
		ppEnabledExtensionNames[offset] = glfwExtensions[offset];
	}
	if (logger->is_enabled()) {
		ppEnabledExtensionNames[offset++] = VK_EXT_DEBUG_UTILS_EXTENSION_NAME;
	}

	logger->print("extensions to be requested:");
	logger->print_list(ppEnabledExtensionNames, enabledExtensionCount);

	/*
	* Layers
	*/
	uint32_t enabledLayerCount = 0;
	if (logger->is_enabled()) {
		enabledLayerCount++;
	}
	const char** ppEnabledLayerNames = nullptr;
	if (enabledLayerCount > 0) {
		ppEnabledLayerNames = (const char**)malloc(enabledLayerCount * sizeof(char*));
	}

	if (logger->is_enabled()) {
		ppEnabledLayerNames[0] = "VK_LAYER_KHRONOS_validation";
	}

	logger->print("layers to be requested:");
	logger->print_list(ppEnabledLayerNames, enabledLayerCount);

	if (!supported_by_instance(ppEnabledExtensionNames, enabledExtensionCount, ppEnabledLayerNames, enabledLayerCount)) {
		return nullptr;
	}

	/*
	*
	* from vulkan_structs.hpp:
	*
	* InstanceCreateInfo( VULKAN_HPP_NAMESPACE::InstanceCreateFlags     flags_                 = {},
										 const VULKAN_HPP_NAMESPACE::ApplicationInfo * pApplicationInfo_      = {},
										 uint32_t                                      enabledLayerCount_     = {},
										 const char * const *                          ppEnabledLayerNames_   = {},
										 uint32_t                                      enabledExtensionCount_ = {},
										 const char * const * ppEnabledExtensionNames_ = {} )
	*/
	vk::InstanceCreateInfo createInfo = vk::InstanceCreateInfo(
		vk::InstanceCreateFlags(),
		&appInfo,
		enabledLayerCount, ppEnabledLayerNames,
		enabledExtensionCount, ppEnabledExtensionNames
	);

	vk::ResultValue<vk::Instance> instanceAttempt= vk::createInstance(createInfo);
	if (instanceAttempt.result != vk::Result::eSuccess) {
		logger->print("Failed to create Instance!");
		return nullptr;
	}

	vk::Instance instance = instanceAttempt.value;

	deletionQueue.push_back([logger](vk::Instance instance) {
		instance.destroy();
		logger->print("Deleted Instance!");
		});
	
	free(ppEnabledExtensionNames);
	if (ppEnabledLayerNames) {
		free(ppEnabledLayerNames);
	}
	return instance;
}