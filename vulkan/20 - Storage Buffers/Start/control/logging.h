#pragma once
#include "../config.h"

namespace vkLogging {

	class Logger {
	public:
		static Logger* logger;
		static Logger* get_logger();
		void set_debug_mode(bool mode);
		bool get_debug_mode();
		//void log_device_properties(vk::PhysicalDevice physical_device);
		void print(std::string message);
		void print_list(std::vector<std::string> items);
		//void log_device_properties(vk::PhysicalDevice device);
		//void log_surface_capabilities(vk::SurfaceCapabilitiesKHR surfaceCapabilities);
		//void log_surface_format(vk::SurfaceFormatKHR surfaceFormat);
	private:
		//std::array<int, 4> extract_version_number;
		//std::string extract_driver_version_nvidia;
		//std::string extract_driver_version_intel;
		//std::string extract_driver_version_standard;
		//void log_physical_device_limits(vk::PhysicalDeviceLimits limits);
		//std::vector<std::string> log_transform_bits(vk::SurfaceTransformFlagsKHR bits);
		//std::vector<std::string> log_alpha_composite_bits(vk::CompositeAlphaFlagsKHR bits);
		//std::vector<std::string> log_image_usage_bits(vk::ImageUsageFlags bits);
		//std::string log_present_mode(vk::PresentModeKHR presentMode);
		bool debugMode;
	};

	/**
		Logging callback function.

		\param messageSeverity describes the severity level of the message
		\param messageType describes the type of the message
		\param pCallbackData standard data associated with the message
		\param pUserData custom extra data which can be associated with the message
		\returns whether to end program execution
	*/
	VKAPI_ATTR VkBool32 VKAPI_CALL debugCallback(
		VkDebugUtilsMessageSeverityFlagBitsEXT messageSeverity,
		VkDebugUtilsMessageTypeFlagsEXT messageType,
		const VkDebugUtilsMessengerCallbackDataEXT* pCallbackData,
		void* pUserData
	);

	/**
		Make a debug messenger

		\param instance The Vulkan instance which will be debugged.
		\param dldi dynamically loads instance based dispatch functions
		\returns the created messenger
	*/
	vk::DebugUtilsMessengerEXT make_debug_messenger(
		vk::Instance& instance, vk::DispatchLoaderDynamic& dldi
	);

	/**
		Extract the transforms from the given bitmask.

		\param bits a bitmask describing various transforms
		\returns a vector of strings describing the transforms
	*/
	std::vector<std::string> log_transform_bits(vk::SurfaceTransformFlagsKHR bits);

	/**
		Extract the alpha composite blend modes from the given bitmask.

		\param bits a bitmask describing a combination of alpha composite options.
		\returns a vector of strings describing the options.
	*/
	std::vector<std::string> log_alpha_composite_bits(vk::CompositeAlphaFlagsKHR bits);

	/**
		Extract image usage options.

		\param bits a bitmask describing various image usages
		\returns a vector of strings describing the image usages
	*/
	std::vector<std::string> log_image_usage_bits(vk::ImageUsageFlags bits);

	/**
		\returns a string description of the given present mode.
	*/
	std::string log_present_mode(vk::PresentModeKHR presentMode);

	/**
		Print out the properties of the given physical device.

		\param device the physical device to investigate
	*/
	void log_device_properties(const vk::PhysicalDevice& device);

}