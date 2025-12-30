#include "instance.h"
#include "../logging/logger.h"
#include <GLFW/glfw3.h>
#include <sstream>
#include <cstdlib>

bool supported_by_instance(DynamicArray<const char*> extensionNames,
	DynamicArray<const char*> layerNames) {

	Logger* logger = Logger::get_logger();
	std::stringstream lineBuilder;

	//check extension support
	DynamicArray<vk::ExtensionProperties> supportedExtensions;
	uint32_t count;
	vk::enumerateInstanceExtensionProperties(NULL, &count, NULL);
	supportedExtensions.resize(count);
	vk::enumerateInstanceExtensionProperties(NULL, &count, supportedExtensions.data);

	logger->print("Instance can support the following extensions:");
	logger->print(supportedExtensions);

	bool found;
	for (int i = 0; i < extensionNames.size; ++i) {
		const char* extension = extensionNames[i];
		found = false;
		for (size_t j = 0; j < supportedExtensions.size; ++j) {
			vk::ExtensionProperties supportedExtension = supportedExtensions[j];

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
	DynamicArray<vk::LayerProperties> supportedLayers;
	vk::enumerateInstanceLayerProperties(&count, NULL);
	supportedLayers.resize(count);
	vk::enumerateInstanceLayerProperties(&count, supportedLayers.data);

	logger->print("Instance can support the following layers:");
	logger->print(supportedLayers);

	for (int i = 0; i < layerNames.size; ++i) {
		const char* layer = layerNames[i];
		found = false;
		for (size_t j = 0; j < supportedLayers.size; ++j) {
			vk::LayerProperties supportedLayer = supportedLayers[j];
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

vk::Instance make_instance(const char* applicationName,
	std::deque<std::function<void(vk::Instance)>>& deletionQueue) {

	Logger* logger = Logger::get_logger();

	logger->print("Making an instance...");

	uint32_t version = vk::makeApiVersion(0, 1, 3, 0);

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

	DynamicArray<const char*> enabledExtensionNames;

	for (size_t i = 0; i < glfwExtensionCount; ++i) {
		enabledExtensionNames.push_back(glfwExtensions[i]);
	}
	if (logger->is_enabled()) {
		enabledExtensionNames.push_back(VK_EXT_DEBUG_UTILS_EXTENSION_NAME);
	}

	logger->print("extensions to be requested:");
	logger->print(enabledExtensionNames);

	/*
	* Layers
	*/
	DynamicArray<const char*> enabledLayerNames;
	if (logger->is_enabled()) {
		enabledLayerNames.push_back("VK_LAYER_KHRONOS_validation");
	}

	logger->print("layers to be requested:");
	logger->print(enabledLayerNames);

	if (!supported_by_instance(enabledExtensionNames, enabledLayerNames)) {
		return nullptr;
	}

	vk::InstanceCreateInfo createInfo = vk::InstanceCreateInfo(
		vk::InstanceCreateFlags(),
		&appInfo,
		enabledLayerNames.size, enabledLayerNames.data,
		enabledExtensionNames.size, enabledExtensionNames.data
	);

	vk::ResultValue<vk::Instance> instanceAttempt =
		vk::createInstance(createInfo);
	if (instanceAttempt.result != vk::Result::eSuccess) {
		logger->print("Failed to create Instance!");
		return nullptr;
	}

	vk::Instance instance = instanceAttempt.value;

	deletionQueue.push_back([logger](vk::Instance instance) {
		instance.destroy();
		logger->print("Deleted Instance!");
		});
	
	return instance;
}