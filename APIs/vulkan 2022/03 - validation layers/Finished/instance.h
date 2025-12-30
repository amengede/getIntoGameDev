#pragma once
#include "config.h"

//namespace for creation functions/definitions etc.
namespace vkInit {

	/**
		Check whether the requested extensions and layers are supported.

		\param extensions a list of extension names being requested.
		\param layers a list of layer names being requested.
		\param debug whether to log error messages.
		\returns whether all of the extensions and layers are supported.
	*/
	bool supported(std::vector<const char*>& extensions, std::vector<const char*>& layers, bool debug);

	/**
		Create a Vulkan instance.

		\param debug whether the system is being run in debug mode.
		\param applicationName the name of the application.
		\returns the instance created.
	*/
	vk::Instance make_instance(bool debug, const char* applicationName);
}