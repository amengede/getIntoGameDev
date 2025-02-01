#include "instance.h"
#include "../logging/logger.h"
#include <GLFW/glfw3.h>

vk::Instance make_instance(const char* applicationName, std::deque<std::function<void()>>& deletionQueue) {

	Logger* logger = Logger::get_logger();

	logger->print("Making an instance...");

	uint32_t version = vk::enumerateInstanceVersion().value;

	logger->report_version_number(version);

	// set the patch to 0 for best compatibility/stability)
	version &= ~(0xFFFU);

	/*
	* from vulkan_structs.hpp:
	*
	* VULKAN_HPP_CONSTEXPR ApplicationInfo( const char * pApplicationName_   = {},
									  uint32_t     applicationVersion_ = {},
									  const char * pEngineName_        = {},
									  uint32_t     engineVersion_      = {},
									  uint32_t     apiVersion_         = {} )
	*/
	vk::ApplicationInfo appInfo = vk::ApplicationInfo(
		applicationName,
		version,
		"Doing it the hard way",
		version,
		version
	);

	/*
	* Everything with Vulkan is "opt-in", so we need to query which extensions glfw needs
	* in order to interface with vulkan.
	*/
	uint32_t glfwExtensionCount = 0;
	const char** glfwExtensions;
	glfwExtensions = glfwGetRequiredInstanceExtensions(&glfwExtensionCount);

	logger->print("extensions to be requested:");
	logger->print_list(glfwExtensions, glfwExtensionCount);

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
		0, nullptr, // enabled layers
		glfwExtensionCount, glfwExtensions // enabled extensions
	);

	vk::ResultValue<vk::Instance> instanceAttempt= vk::createInstance(createInfo);
	if (instanceAttempt.result != vk::Result::eSuccess) {
		logger->print("Failed to create Instance!");
		return nullptr;
	}

	vk::Instance instance = instanceAttempt.value;
	VkInstance handle = instance;

	deletionQueue.push_back([logger, handle]() {
		vkDestroyInstance(handle, nullptr);
		logger->print("Deleted Instance!");
		});
	
	return instance;
}