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