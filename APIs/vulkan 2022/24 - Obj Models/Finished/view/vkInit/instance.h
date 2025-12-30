#pragma once
#include "../../control/logging.h"
#include "../../config.h"

//namespace for creation functions/definitions etc.
namespace vkInit {

	/**
		Check whether the requested extensions and layers are supported.

		\param extensions a list of extension names being requested.
		\param layers a list of layer names being requested.
		\returns whether all of the extensions and layers are supported.
	*/
	bool supported(std::vector<const char*>& extensions, std::vector<const char*>& layers) {
		
		std::stringstream message;
		//check extension support
		std::vector<vk::ExtensionProperties> supportedExtensions = vk::enumerateInstanceExtensionProperties();

		vkLogging::Logger::get_logger()->print("Device can support the following extensions:");
		if (vkLogging::Logger::get_logger()->get_debug_mode()) {
			for (vk::ExtensionProperties supportedExtension : supportedExtensions) {
				std::cout << '\t' << supportedExtension.extensionName << '\n';
			}
		}

		bool found;
		for (const char* extension : extensions) {
			found = false;
			for (vk::ExtensionProperties supportedExtension : supportedExtensions) {
				if (strcmp(extension, supportedExtension.extensionName) == 0) {
					found = true;
					message << "Extension \"" << extension << "\" is supported!";
					vkLogging::Logger::get_logger()->print(message.str());
					message.str("");
				}
			}
			if (!found) {
				message << "Extension \"" << extension << "\" is not supported!";
				vkLogging::Logger::get_logger()->print(message.str());
				message.str("");
				return false;
			}
		}

		//check layer support
		std::vector<vk::LayerProperties> supportedLayers = vk::enumerateInstanceLayerProperties();

		vkLogging::Logger::get_logger()->print("Device can support the following layers:");
		if (vkLogging::Logger::get_logger()->get_debug_mode()) {
			for (vk::LayerProperties supportedLayer : supportedLayers) {
				std::cout << '\t' << supportedLayer.layerName << '\n';
			}
		}

		for (const char* layer : layers) {
			found = false;
			for (vk::LayerProperties supportedLayer : supportedLayers) {
				if (strcmp(layer, supportedLayer.layerName) == 0) {
					found = true;
					message << "Layer \"" << layer << "\" is supported!";
					vkLogging::Logger::get_logger()->print(message.str());
					message.str("");
				}
			}
			if (!found) {
				message << "Layer \"" << layer << "\" is not supported!";
				vkLogging::Logger::get_logger()->print(message.str());
				message.str("");
				return false;
			}
		}

		return true;
	}

	/**
		Create a Vulkan instance.

		\param applicationName the name of the application.
		\returns the instance created.
	*/
	vk::Instance make_instance(const char* applicationName) {

		vkLogging::Logger::get_logger()->print("Making an instance...");

		/*
		* An instance stores all per-application state info, it is a vulkan handle
		* (An opaque integer or pointer value used to refer to a Vulkan object)
		* side note: in the vulkan.hpp binding it's a wrapper class around a handle
		*
		* from vulkan_core.h:
		* VK_DEFINE_HANDLE(VkInstance)
		*
		* from vulkan_handles.hpp:
		* class Instance {
		* ...
		* }
		*/

		/*
		* We can scan the system and check which version it will support up to,
		* as of vulkan 1.1
		*
		* VkResult vkEnumerateInstanceVersion(
			uint32_t*                                   pApiVersion);
		*/

		uint32_t version{ 0 };
		vkEnumerateInstanceVersion(&version);

		if (vkLogging::Logger::get_logger()->get_debug_mode()) {
			std::cout << "System can support vulkan Variant: " << VK_API_VERSION_VARIANT(version)
				<< ", Major: " << VK_API_VERSION_MAJOR(version)
				<< ", Minor: " << VK_API_VERSION_MINOR(version)
				<< ", Patch: " << VK_API_VERSION_PATCH(version) << '\n';
		}

		/*
		* We can then either use this version
		* (We shoud just be sure to set the patch to 0 for best compatibility/stability)
		*/
		version &= ~(0xFFFU);

		/*
		* Or drop down to an earlier version to ensure compatibility with more devices
		* VK_MAKE_API_VERSION(variant, major, minor, patch)
		*/
		version = VK_MAKE_API_VERSION(0, 1, 1, 0);

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

		std::vector<const char*> extensions(glfwExtensions, glfwExtensions + glfwExtensionCount);

		//In order to hook in a custom validation callback
		if (vkLogging::Logger::get_logger()->get_debug_mode()) {
			extensions.push_back("VK_EXT_debug_utils");
		}

		vkLogging::Logger::get_logger()->print("extensions to be requested:");
		if (vkLogging::Logger::get_logger()->get_debug_mode()) {

			for (const char* extensionName : extensions) {
				std::cout << "\t\"" << extensionName << "\"\n";
			}
		}

		std::vector<const char*> layers;
		if (vkLogging::Logger::get_logger()->get_debug_mode()) {
			layers.push_back("VK_LAYER_KHRONOS_validation");
		}

		if (!supported(extensions, layers)) {
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
			static_cast<uint32_t>(layers.size()), layers.data(), // enabled layers
			static_cast<uint32_t>(extensions.size()), extensions.data() // enabled extensions
		);


		try {
			/*
			* from vulkan_funcs.h:
			* 
			* createInstance( const VULKAN_HPP_NAMESPACE::InstanceCreateInfo &          createInfo,
                    Optional<const VULKAN_HPP_NAMESPACE::AllocationCallbacks> allocator = nullptr,
                    Dispatch const &                                          d = ::vk::getDispatchLoaderStatic())
				
			*/
			return vk::createInstance(createInfo);
		}
		catch (vk::SystemError err) {
			vkLogging::Logger::get_logger()->print("Failed to create Instance!");
			return nullptr;
		}
	}
}