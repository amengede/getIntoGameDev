#pragma once
#include "config.h"

namespace vkInit {

	/*
	* Debug call back:
	*
	*	typedef enum VkDebugUtilsMessageSeverityFlagBitsEXT {
			VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT = 0x00000001,
			VK_DEBUG_UTILS_MESSAGE_SEVERITY_INFO_BIT_EXT = 0x00000010,
			VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT = 0x00000100,
			VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT = 0x00001000,
			VK_DEBUG_UTILS_MESSAGE_SEVERITY_FLAG_BITS_MAX_ENUM_EXT = 0x7FFFFFFF
		} VkDebugUtilsMessageSeverityFlagBitsEXT;

	*	typedef enum VkDebugUtilsMessageTypeFlagBitsEXT {
			VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT = 0x00000001,
			VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT = 0x00000002,
			VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT = 0x00000004,
			VK_DEBUG_UTILS_MESSAGE_TYPE_FLAG_BITS_MAX_ENUM_EXT = 0x7FFFFFFF
		} VkDebugUtilsMessageTypeFlagBitsEXT;

	*	typedef struct VkDebugUtilsMessengerCallbackDataEXT {
			VkStructureType                              sType;
			const void*                                  pNext;
			VkDebugUtilsMessengerCallbackDataFlagsEXT    flags;
			const char*                                  pMessageIdName;
			int32_t                                      messageIdNumber;
			const char*                                  pMessage;
			uint32_t                                     queueLabelCount;
			const VkDebugUtilsLabelEXT*                  pQueueLabels;
			uint32_t                                     cmdBufLabelCount;
			const VkDebugUtilsLabelEXT*                  pCmdBufLabels;
			uint32_t                                     objectCount;
			const VkDebugUtilsObjectNameInfoEXT*         pObjects;
		} VkDebugUtilsMessengerCallbackDataEXT;

	*/
	VKAPI_ATTR VkBool32 VKAPI_CALL debugCallback(
		VkDebugUtilsMessageSeverityFlagBitsEXT messageSeverity,
		VkDebugUtilsMessageTypeFlagsEXT messageType,
		const VkDebugUtilsMessengerCallbackDataEXT* pCallbackData,
		void* pUserData
	) {
		std::cerr << "validation layer: " << pCallbackData->pMessage << std::endl;

		return VK_FALSE;
	}

	vk::DebugUtilsMessengerEXT make_debug_messenger(vk::Instance& instance, vk::DispatchLoaderDynamic& dldi) {

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
			debugCallback,
			nullptr
		);

		return instance.createDebugUtilsMessengerEXT(createInfo, nullptr, dldi);
	}
}