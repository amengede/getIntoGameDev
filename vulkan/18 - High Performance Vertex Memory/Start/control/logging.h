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

	VKAPI_ATTR VkBool32 VKAPI_CALL debugCallback(
		VkDebugUtilsMessageSeverityFlagBitsEXT messageSeverity,
		VkDebugUtilsMessageTypeFlagsEXT messageType,
		const VkDebugUtilsMessengerCallbackDataEXT* pCallbackData,
		void* pUserData
	);

	vk::DebugUtilsMessengerEXT make_debug_messenger(
		vk::Instance& instance, vk::DispatchLoaderDynamic& dldi
	);

	/**
	* Extract the transform types contained within the given bitmask
	* 
	* @param bits	the bitmask which holds various transforms
	* @return		a vector of strings describing the transforms
	*/
	std::vector<std::string> log_transform_bits(vk::SurfaceTransformFlagsKHR bits);

	/**
	* Extract the alpha composite types contained within the given bitmask
	*
	* @param bits	the bitmask which holds various alpha composite modes
	* @return		a vector of strings describing the alpha composite modes
	*/
	std::vector<std::string> log_alpha_composite_bits(vk::CompositeAlphaFlagsKHR bits);

	/**
	* Extract the image usages contained within the given bitmask
	*
	* @param bits	the bitmask which holds various image usages
	* @return		a vector of strings describing the image usages
	*/
	std::vector<std::string> log_image_usage_bits(vk::ImageUsageFlags bits);

	/**
	* Translate the given present mode to a dexcriptive string
	*
	* @param presentMode	an enum which describes the present mode
	* @return				a description of the present mode
	*/
	std::string log_present_mode(vk::PresentModeKHR presentMode);

	/**
	* Print out some properties of a physical device
	*
	* @param device the physical device
	*/
	void log_device_properties(const vk::PhysicalDevice& device);

}