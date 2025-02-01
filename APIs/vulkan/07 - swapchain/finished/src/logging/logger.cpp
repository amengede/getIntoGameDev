#include <iostream>
#include "logger.h"

Logger* Logger::logger;

VKAPI_ATTR VkBool32 VKAPI_CALL debugCallback(
	VkDebugUtilsMessageSeverityFlagBitsEXT messageSeverity,
	VkDebugUtilsMessageTypeFlagsEXT messageType,
	const VkDebugUtilsMessengerCallbackDataEXT* pCallbackData,
	void* pUserData) {
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
	vk::Instance& instance, vk::DispatchLoaderDynamic& dldi,
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
		debugCallback,
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

void Logger::log(const vk::PhysicalDevice& device) {

	if (!enabled) {
		return;
	}
	vk::PhysicalDeviceProperties properties = device.getProperties();

	std::cout << "Device name: " << properties.deviceName << std::endl;

	std::cout << "Device type: ";
	switch (properties.deviceType) {

	case (vk::PhysicalDeviceType::eCpu):
		std::cout << "CPU";
		break;

	case (vk::PhysicalDeviceType::eDiscreteGpu):
		std::cout << "Discrete GPU";
		break;

	case (vk::PhysicalDeviceType::eIntegratedGpu):
		std::cout << "Integrated GPU";
		break;

	case (vk::PhysicalDeviceType::eVirtualGpu):
		std::cout << "Virtual GPU";
		break;

	default:
		std::cout << "Other";
	}
	std::cout << std::endl;
}

void Logger::log(const std::vector<vk::QueueFamilyProperties>& queueFamilies) {

	if (!enabled) {
		return;
	}

	std::cout << "There are " << queueFamilies.size() 
		<< " queue families available on the system." 
		<< std::endl;
	
	for (uint32_t i = 0; i < queueFamilies.size(); ++i) {

		/*
		* // Provided by VK_VERSION_1_0
			typedef struct VkQueueFamilyProperties {
			VkQueueFlags    queueFlags;
			uint32_t        queueCount;
			uint32_t        timestampValidBits;
			VkExtent3D      minImageTransferGranularity;
			} VkQueueFamilyProperties;

			queueFlags is a bitmask of VkQueueFlagBits indicating capabilities of the queues in this queue family.

			queueCount is the unsigned integer count of queues in this queue family. Each queue family must support 
			at least one queue.
		*/

		/*
		* // Provided by VK_VERSION_1_0
			typedef enum VkQueueFlagBits {
			VK_QUEUE_GRAPHICS_BIT = 0x00000001,
			VK_QUEUE_COMPUTE_BIT = 0x00000002,
			VK_QUEUE_TRANSFER_BIT = 0x00000004,
			VK_QUEUE_SPARSE_BINDING_BIT = 0x00000008,
			} VkQueueFlagBits;
		*/

		vk::QueueFamilyProperties queueFamily = queueFamilies[i];

		std::cout << "Queue Family " << i << ":" << std::endl;

		std::cout << "\tSupports ";
		if (queueFamily.queueFlags & vk::QueueFlagBits::eCompute) {
			std::cout << "compute, ";
		}
		if (queueFamily.queueFlags & vk::QueueFlagBits::eGraphics) {
			std::cout << "graphics, ";
		}
		if (queueFamily.queueFlags & vk::QueueFlagBits::eTransfer) {
			std::cout << "transfer, ";
		}
		if (queueFamily.queueFlags & vk::QueueFlagBits::eOpticalFlowNV) {
			std::cout << "nvidia optical flow, ";
		}
		if (queueFamily.queueFlags & vk::QueueFlagBits::eSparseBinding) {
			std::cout << "sparse binding, ";
		}
		if (queueFamily.queueFlags & vk::QueueFlagBits::eProtected) {
			std::cout << "protected memory, ";
		}
		if (queueFamily.queueFlags & vk::QueueFlagBits::eVideoDecodeKHR) {
			std::cout << "video decode, ";
		}
		if (queueFamily.queueFlags & vk::QueueFlagBits::eVideoEncodeKHR) {
			std::cout << "video encode, ";
		}
		std::cout << std::endl;

		std::cout << "\tFamily supports " 
			<< queueFamily.queueCount << " queues." << std::endl;
	}
}

void Logger::log(const vk::SurfaceCapabilitiesKHR& capabilities) {

	if (!enabled) {
		return;
	}

	/*
	* typedef struct VkSurfaceCapabilitiesKHR {
		uint32_t                         minImageCount;
		uint32_t                         maxImageCount;
		VkExtent2D                       currentExtent;
		VkExtent2D                       minImageExtent;
		VkExtent2D                       maxImageExtent;
		uint32_t                         maxImageArrayLayers;
		VkSurfaceTransformFlagsKHR       supportedTransforms;
		VkSurfaceTransformFlagBitsKHR    currentTransform;
		VkCompositeAlphaFlagsKHR         supportedCompositeAlpha;
		VkImageUsageFlags                supportedUsageFlags;
	} VkSurfaceCapabilitiesKHR;
	*/
	std::cout << "Swapchain can support the following surface capabilities:" << std::endl;

	std::cout << "\tminimum image count: " 
			<< capabilities.minImageCount << std::endl;
	std::cout << "\tmaximum image count: " 
			<< capabilities.maxImageCount << std::endl;

	std::cout << "\tcurrent extent:" << std::endl;
	log(capabilities.currentExtent, "\t\t");

	std::cout << "\tminimum supported extent:" << std::endl;
	log(capabilities.minImageExtent, "\t\t");

	std::cout << "\tmaximum supported extent:" << std::endl;
	log(capabilities.maxImageExtent, "\t\t");

	std::cout << "\tmaximum image array layers: " 
		<< capabilities.maxImageArrayLayers << std::endl;

	std::cout << "\tsupported transforms:" << std::endl;
	std::vector<std::string> stringList = 
		parse_transform_bits(capabilities.supportedTransforms);
	log(stringList, "\t\t");

	std::cout << "\tcurrent transform:" << std::endl;
	stringList = parse_transform_bits(capabilities.currentTransform);
	log(stringList, "\t\t");

	std::cout << "\tsupported alpha operations:" << std::endl;
	stringList = parse_alpha_composite_bits(capabilities.supportedCompositeAlpha);
	log(stringList, "\t\t");

	std::cout << "\tsupported image usage:" << std::endl;
	stringList = parse_image_usage_bits(capabilities.supportedUsageFlags);
	log(stringList, "\t\t");
}

void Logger::log(const vk::Extent2D& extent, const char* prefix) {
	
	if (!enabled) {
		return;
	}

	/*typedef struct VkExtent2D {
		uint32_t    width;
		uint32_t    height;
	} VkExtent2D;
	*/

	std::cout << prefix << "width: " << extent.width << std::endl;
	std::cout << prefix << "height: " << extent.height << std::endl;
}

std::vector<std::string> Logger::parse_transform_bits(
	vk::SurfaceTransformFlagsKHR bits) {
	
	std::vector<std::string> result;

	/*
	* typedef enum VkSurfaceTransformFlagBitsKHR {
		VK_SURFACE_TRANSFORM_IDENTITY_BIT_KHR = 0x00000001,
		VK_SURFACE_TRANSFORM_ROTATE_90_BIT_KHR = 0x00000002,
		VK_SURFACE_TRANSFORM_ROTATE_180_BIT_KHR = 0x00000004,
		VK_SURFACE_TRANSFORM_ROTATE_270_BIT_KHR = 0x00000008,
		VK_SURFACE_TRANSFORM_HORIZONTAL_MIRROR_BIT_KHR = 0x00000010,
		VK_SURFACE_TRANSFORM_HORIZONTAL_MIRROR_ROTATE_90_BIT_KHR = 0x00000020,
		VK_SURFACE_TRANSFORM_HORIZONTAL_MIRROR_ROTATE_180_BIT_KHR = 0x00000040,
		VK_SURFACE_TRANSFORM_HORIZONTAL_MIRROR_ROTATE_270_BIT_KHR = 0x00000080,
		VK_SURFACE_TRANSFORM_INHERIT_BIT_KHR = 0x00000100,
	} VkSurfaceTransformFlagBitsKHR;
	*/
	if (bits & vk::SurfaceTransformFlagBitsKHR::eIdentity) {
		result.push_back("identity");
	}
	if (bits & vk::SurfaceTransformFlagBitsKHR::eRotate90) {
		result.push_back("90 degree rotation");
	}
	if (bits & vk::SurfaceTransformFlagBitsKHR::eRotate180) {
		result.push_back("180 degree rotation");
	}
	if (bits & vk::SurfaceTransformFlagBitsKHR::eRotate270) {
		result.push_back("270 degree rotation");
	}
	if (bits & vk::SurfaceTransformFlagBitsKHR::eHorizontalMirror) {
		result.push_back("horizontal mirror");
	}
	if (bits & vk::SurfaceTransformFlagBitsKHR::eHorizontalMirrorRotate90) {
		result.push_back("horizontal mirror, then 90 degree rotation");
	}
	if (bits & vk::SurfaceTransformFlagBitsKHR::eHorizontalMirrorRotate180) {
		result.push_back("horizontal mirror, then 180 degree rotation");
	}
	if (bits & vk::SurfaceTransformFlagBitsKHR::eHorizontalMirrorRotate270) {
		result.push_back("horizontal mirror, then 270 degree rotation");
	}
	if (bits & vk::SurfaceTransformFlagBitsKHR::eInherit) {
		result.push_back("inherited");
	}
	return result;
}

std::vector<std::string> Logger::parse_alpha_composite_bits(
	vk::CompositeAlphaFlagsKHR bits) {
	
	std::vector<std::string> result;

	/*
		typedef enum VkCompositeAlphaFlagBitsKHR {
			VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR = 0x00000001,
			VK_COMPOSITE_ALPHA_PRE_MULTIPLIED_BIT_KHR = 0x00000002,
			VK_COMPOSITE_ALPHA_POST_MULTIPLIED_BIT_KHR = 0x00000004,
			VK_COMPOSITE_ALPHA_INHERIT_BIT_KHR = 0x00000008,
		} VkCompositeAlphaFlagBitsKHR;
	*/
	if (bits & vk::CompositeAlphaFlagBitsKHR::eOpaque) {
		result.push_back("opaque (alpha ignored)");
	}
	if (bits & vk::CompositeAlphaFlagBitsKHR::ePreMultiplied) {
		result.push_back("pre multiplied (alpha expected to already be multiplied in image)");
	}
	if (bits & vk::CompositeAlphaFlagBitsKHR::ePostMultiplied) {
		result.push_back("post multiplied (alpha will be applied during composition)");
	}
	if (bits & vk::CompositeAlphaFlagBitsKHR::eInherit) {
		result.push_back("inherited");
	}

	return result;
}

std::vector<std::string> Logger::parse_image_usage_bits(
	vk::ImageUsageFlags bits) {
	
	std::vector<std::string> result;

	/*
		typedef enum VkImageUsageFlagBits {
			VK_IMAGE_USAGE_TRANSFER_SRC_BIT = 0x00000001,
			VK_IMAGE_USAGE_TRANSFER_DST_BIT = 0x00000002,
			VK_IMAGE_USAGE_SAMPLED_BIT = 0x00000004,
			VK_IMAGE_USAGE_STORAGE_BIT = 0x00000008,
			VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT = 0x00000010,
			VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT = 0x00000020,
			VK_IMAGE_USAGE_TRANSIENT_ATTACHMENT_BIT = 0x00000040,
			VK_IMAGE_USAGE_INPUT_ATTACHMENT_BIT = 0x00000080,
			#ifdef VK_ENABLE_BETA_EXTENSIONS
				// Provided by VK_KHR_video_decode_queue
				VK_IMAGE_USAGE_VIDEO_DECODE_DST_BIT_KHR = 0x00000400,
			#endif
			#ifdef VK_ENABLE_BETA_EXTENSIONS
				// Provided by VK_KHR_video_decode_queue
				VK_IMAGE_USAGE_VIDEO_DECODE_SRC_BIT_KHR = 0x00000800,
			#endif
			#ifdef VK_ENABLE_BETA_EXTENSIONS
				// Provided by VK_KHR_video_decode_queue
				VK_IMAGE_USAGE_VIDEO_DECODE_DPB_BIT_KHR = 0x00001000,
			#endif
			// Provided by VK_EXT_fragment_density_map
			VK_IMAGE_USAGE_FRAGMENT_DENSITY_MAP_BIT_EXT = 0x00000200,
			// Provided by VK_KHR_fragment_shading_rate
			VK_IMAGE_USAGE_FRAGMENT_SHADING_RATE_ATTACHMENT_BIT_KHR = 0x00000100,
			#ifdef VK_ENABLE_BETA_EXTENSIONS
				// Provided by VK_KHR_video_encode_queue
				VK_IMAGE_USAGE_VIDEO_ENCODE_DST_BIT_KHR = 0x00002000,
			#endif
			#ifdef VK_ENABLE_BETA_EXTENSIONS
				// Provided by VK_KHR_video_encode_queue
				VK_IMAGE_USAGE_VIDEO_ENCODE_SRC_BIT_KHR = 0x00004000,
			#endif
			#ifdef VK_ENABLE_BETA_EXTENSIONS
				// Provided by VK_KHR_video_encode_queue
				VK_IMAGE_USAGE_VIDEO_ENCODE_DPB_BIT_KHR = 0x00008000,
			#endif
			// Provided by VK_HUAWEI_invocation_mask
			VK_IMAGE_USAGE_INVOCATION_MASK_BIT_HUAWEI = 0x00040000,
			// Provided by VK_NV_shading_rate_image
			VK_IMAGE_USAGE_SHADING_RATE_IMAGE_BIT_NV = VK_IMAGE_USAGE_FRAGMENT_SHADING_RATE_ATTACHMENT_BIT_KHR,
	} VkImageUsageFlagBits;
	*/
	if (bits & vk::ImageUsageFlagBits::eTransferSrc) {
		result.push_back("transfer src: image can be used as the source of a transfer command.");
	}
	if (bits & vk::ImageUsageFlagBits::eTransferDst) {
		result.push_back("transfer dst: image can be used as the destination of a transfer command.");
	}
	if (bits & vk::ImageUsageFlagBits::eSampled) {
		result.push_back("sampled: image can be used to create a VkImageView suitable for occupying a \
VkDescriptorSet slot either of type VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE or \
VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER, and be sampled by a shader.");
	}
	if (bits & vk::ImageUsageFlagBits::eStorage) {
		result.push_back("storage: image can be used to create a VkImageView suitable for occupying a \
VkDescriptorSet slot of type VK_DESCRIPTOR_TYPE_STORAGE_IMAGE.");
	}
	if (bits & vk::ImageUsageFlagBits::eColorAttachment) {
		result.push_back("color attachment: image can be used to create a VkImageView suitable for use as \
a color or resolve attachment in a VkFramebuffer.");
	}
	if (bits & vk::ImageUsageFlagBits::eDepthStencilAttachment) {
		result.push_back("depth/stencil attachment: image can be used to create a VkImageView \
suitable for use as a depth/stencil or depth/stencil resolve attachment in a VkFramebuffer.");
	}
	if (bits & vk::ImageUsageFlagBits::eTransientAttachment) {
		result.push_back("transient attachment: implementations may support using memory allocations \
with the VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT to back an image with this usage. This \
bit can be set for any image that can be used to create a VkImageView suitable for use as \
a color, resolve, depth/stencil, or input attachment.");
	}
	if (bits & vk::ImageUsageFlagBits::eInputAttachment) {
		result.push_back("input attachment: image can be used to create a VkImageView suitable for \
occupying VkDescriptorSet slot of type VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT; be read from \
a shader as an input attachment; and be used as an input attachment in a framebuffer.");
	}
	if (bits & vk::ImageUsageFlagBits::eFragmentDensityMapEXT) {
		result.push_back("fragment density map: image can be used to create a VkImageView suitable \
for use as a fragment density map image.");
	}
	if (bits & vk::ImageUsageFlagBits::eFragmentShadingRateAttachmentKHR) {
		result.push_back("fragment shading rate attachment: image can be used to create a VkImageView \
suitable for use as a fragment shading rate attachment or shading rate image");
	}
	return result;
}

void Logger::log(const std::vector<std::string>& items, const char* prefix) {

	if (!enabled) {
		return;
	}

	for (std::string item : items) {
		std::cout << prefix << item << std::endl;
	}
}

void Logger::log(const std::vector<vk::SurfaceFormatKHR>& formats) {

	if (!enabled) {
		return;
	}

	for (vk::SurfaceFormatKHR supportedFormat : formats) {
		/*
		* typedef struct VkSurfaceFormatKHR {
			VkFormat           format;
			VkColorSpaceKHR    colorSpace;
		} VkSurfaceFormatKHR;
		*/

		std::cout << "supported pixel format: " 
			<< vk::to_string(supportedFormat.format) 
			<< ", supported color space: " 
			<< vk::to_string(supportedFormat.colorSpace) 
			<< std::endl;
	}
}

void Logger::log(const std::vector<vk::PresentModeKHR>& modes) {

	if (!enabled) {
		return;
	}

	for (vk::PresentModeKHR presentMode : modes) {
		std::cout << '\t' << vk::to_string(presentMode) << std::endl;
	}
}
