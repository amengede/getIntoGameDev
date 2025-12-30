#pragma once
#include "config.h"
#include "logging.h"

/*
* Vulkan separates the concept of physical and logical devices. 
* 
  A physical device usually represents a single complete implementation of Vulkan 
  (excluding instance-level functionality) available to the host, 
  of which there are a finite number. 
  
  A logical device represents an instance of that implementation 
  with its own state and resources independent of other logical devices.
*/

namespace vkInit {

	/**
		Holds the indices of the graphics and presentation queue families.
	*/
	struct QueueFamilyIndices {
		std::optional<uint32_t> graphicsFamily;
		std::optional<uint32_t> presentFamily;

		/**
			\returns whether all of the Queue family indices have been set.
		*/
		bool isComplete() {
			return graphicsFamily.has_value() && presentFamily.has_value();
		}
	};

	/**
		Holds properties of the swapchain
		capabilities: no. of images and supported sizes
		formats: eg. supported pixel formats
		present modes: available presentation modes (eg. double buffer, fifo, mailbox)
	*/
	struct SwapChainSupportDetails {
		vk::SurfaceCapabilitiesKHR capabilities;
		std::vector<vk::SurfaceFormatKHR> formats;
		std::vector<vk::PresentModeKHR> presentModes;
	};

	/**
		Various data structures associated with the swapchain.
	*/
	struct SwapChainBundle {
		vk::SwapchainKHR swapchain;
		std::vector<vk::Image> images;
		vk::Format format;
		vk::Extent2D extent;
	};

	/**
		Print out the properties of the given physical device.

		\param device the physical device to investigate
	*/
	void log_device_properties(const vk::PhysicalDevice& device) {
		/*
		* void vkGetPhysicalDeviceProperties(
			VkPhysicalDevice                            physicalDevice,
			VkPhysicalDeviceProperties*                 pProperties);
		*/

		vk::PhysicalDeviceProperties properties = device.getProperties();

		/*
		* typedef struct VkPhysicalDeviceProperties {
			uint32_t                            apiVersion;
			uint32_t                            driverVersion;
			uint32_t                            vendorID;
			uint32_t                            deviceID;
			VkPhysicalDeviceType                deviceType;
			char                                deviceName[VK_MAX_PHYSICAL_DEVICE_NAME_SIZE];
			uint8_t                             pipelineCacheUUID[VK_UUID_SIZE];
			VkPhysicalDeviceLimits              limits;
			VkPhysicalDeviceSparseProperties    sparseProperties;
			} VkPhysicalDeviceProperties;
		*/

		std::cout << "Device name: " << properties.deviceName << '\n';

		std::cout << "Device type: ";
		switch (properties.deviceType) {

		case (vk::PhysicalDeviceType::eCpu):
			std::cout << "CPU\n";
			break;

		case (vk::PhysicalDeviceType::eDiscreteGpu):
			std::cout << "Discrete GPU\n";
			break;

		case (vk::PhysicalDeviceType::eIntegratedGpu):
			std::cout << "Integrated GPU\n";
			break;

		case (vk::PhysicalDeviceType::eVirtualGpu):
			std::cout << "Virtual GPU\n";
			break;

		default:
			std::cout << "Other\n";
		}
	}

	/**
		Check whether the physical device can support the given extensions.

		\param device the physical device to check
		\param requestedExtensions a list of extension names to check against
		\param debug whether the system is running in debug mode
		\returns whether all of the extensions are requested
	*/
	bool checkDeviceExtensionSupport(
		const vk::PhysicalDevice& device,
		const std::vector<const char*>& requestedExtensions,
		const bool& debug
	) {

		/*
		* Check if a given physical device can satisfy a list of requested device
		* extensions.
		*/

		std::set<std::string> requiredExtensions(requestedExtensions.begin(), requestedExtensions.end());

		if (debug) {
			std::cout << "Device can support extensions:\n";
		}

		for (vk::ExtensionProperties& extension : device.enumerateDeviceExtensionProperties()) {

			if (debug) {
				std::cout << "\t\"" << extension.extensionName << "\"\n";
			}

			//remove this from the list of required extensions (set checks for equality automatically)
			requiredExtensions.erase(extension.extensionName);
		}

		//if the set is empty then all requirements have been satisfied
		return requiredExtensions.empty();
	}

	/**
		Choose a physical device for the vulkan instance.

		\param instance the vulkan instance to use
		\param debug whether the system is running in debug mode
		\returns the chosen physical device
	*/
	bool isSuitable(const vk::PhysicalDevice& device, const bool debug) {

		if (debug) {
			std::cout << "Checking if device is suitable\n";
		}

		/*
		* A device is suitable if it can present to the screen, ie support
		* the swapchain extension
		*/
		const std::vector<const char*> requestedExtensions = {
			VK_KHR_SWAPCHAIN_EXTENSION_NAME
		};

		if (debug) {
			std::cout << "We are requesting device extensions:\n";

			for (const char* extension : requestedExtensions) {
				std::cout << "\t\"" << extension << "\"\n";
			}

		}

		if (bool extensionsSupported = checkDeviceExtensionSupport(device, requestedExtensions, debug)) {

			if (debug) {
				std::cout << "Device can support the requested extensions!\n";
			}
		}
		else {

			if (debug) {
				std::cout << "Device can't support the requested extensions!\n";
			}

			return false;
		}
		return true;
	}

	/**
		Choose a physical device for the vulkan instance.

		\param instance the vulkan instance to use
		\param debug whether the system is running in debug mode
		\returns the chosen physical device
	*/
	vk::PhysicalDevice choose_physical_device(const vk::Instance& instance, const bool debug) {

		/*
		* Choose a suitable physical device from a list of candidates.
		* Note: Physical devices are neither created nor destroyed, they exist
		* independently to the program.
		*/

		if (debug) {
			std::cout << "Choosing Physical Device\n";
		}

		/*
		* ResultValueType<std::vector<PhysicalDevice, PhysicalDeviceAllocator>>::type
			Instance::enumeratePhysicalDevices( Dispatch const & d )

		  std::vector<vk::PhysicalDevice> instance.enumeratePhysicalDevices( Dispatch const & d = static/default )
		*/
		std::vector<vk::PhysicalDevice> availableDevices = instance.enumeratePhysicalDevices();

		if (debug) {
			std::cout << "There are " << availableDevices.size() << " physical devices available on this system\n";
		}

		/*
		* check if a suitable device can be found
		*/
		for (vk::PhysicalDevice device : availableDevices) {

			if (debug) {
				log_device_properties(device);
			}
			if (isSuitable(device, debug)) {
				return device;
			}
		}

		return nullptr;
	}

	/**
		Find suitable queue family indices on the given physical device.

		\param device the physical device to check
		\param debug whether the system is running in debug mode
		\returns a struct holding the queue family indices
	*/
	QueueFamilyIndices findQueueFamilies(vk::PhysicalDevice device, vk::SurfaceKHR surface, bool debug) {
		QueueFamilyIndices indices;

		std::vector<vk::QueueFamilyProperties> queueFamilies = device.getQueueFamilyProperties();

		if (debug) {
			std::cout << "There are " << queueFamilies.size() << " queue families available on the system.\n";
		}

		int i = 0;
		for (vk::QueueFamilyProperties queueFamily : queueFamilies) {

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

				timestampValidBits is the unsigned integer count of meaningful bits in the timestamps written via 
				vkCmdWriteTimestamp. The valid range for the count is 36..64 bits, or a value of 0, 
				indicating no support for timestamps. Bits outside the valid range are guaranteed to be zeros.

				minImageTransferGranularity is the minimum granularity supported for image transfer 
				operations on the queues in this queue family.
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

			if (queueFamily.queueFlags & vk::QueueFlagBits::eGraphics) {
				indices.graphicsFamily = i;

				if (debug) {
					std::cout << "Queue Family " << i << " is suitable for graphics\n";
				}
			}

			if (device.getSurfaceSupportKHR(i, surface)) {
				indices.presentFamily = i;

				if (debug) {
					std::cout << "Queue Family " << i << " is suitable for presenting\n";
				}
			}

			if (indices.isComplete()) {
				break;
			}

			i++;
		}

		return indices;
	}

	/**
		Create a Vulkan device

		\param physicalDevice the Physical Device to represent
		\param debug whether the system is running in debug mode
		\returns the created device
	*/
	vk::Device create_logical_device(vk::PhysicalDevice physicalDevice, vk::SurfaceKHR surface, bool debug) {

		/*
		* Create an abstraction around the GPU
		*/

		/*
		* At time of creation, any required queues will also be created,
		* so queue create info must be passed in.
		*/

		QueueFamilyIndices indices = findQueueFamilies(physicalDevice, surface, debug);
		std::vector<uint32_t> uniqueIndices;
		uniqueIndices.push_back(indices.graphicsFamily.value());
		if (indices.graphicsFamily.value() != indices.presentFamily.value()) {
			uniqueIndices.push_back(indices.presentFamily.value());
		}
		/*
		* VULKAN_HPP_CONSTEXPR DeviceQueueCreateInfo( VULKAN_HPP_NAMESPACE::DeviceQueueCreateFlags flags_            = {},
                                                uint32_t                                     queueFamilyIndex_ = {},
                                                uint32_t                                     queueCount_       = {},
                                                const float * pQueuePriorities_ = {} ) VULKAN_HPP_NOEXCEPT
		*/
		std::vector<vk::DeviceQueueCreateInfo> queueCreateInfo;
		float queuePriority = 1.0f;
		for (uint32_t queueFamilyIndex : uniqueIndices) {
			queueCreateInfo.push_back(
				vk::DeviceQueueCreateInfo(
					vk::DeviceQueueCreateFlags(), queueFamilyIndex, 1, &queuePriority
				)
			);
		}

		/*
		* Device features must be requested before the device is abstracted,
		* therefore we only pay for what we need.
		*/

		vk::PhysicalDeviceFeatures deviceFeatures = vk::PhysicalDeviceFeatures();

		/*
		* Device extensions to be requested:
		*/
		std::vector<const char*> deviceExtensions = {
			VK_KHR_SWAPCHAIN_EXTENSION_NAME
		};

		/*
		* VULKAN_HPP_CONSTEXPR DeviceCreateInfo( VULKAN_HPP_NAMESPACE::DeviceCreateFlags flags_                         = {},
                                           uint32_t                                queueCreateInfoCount_          = {},
                                           const VULKAN_HPP_NAMESPACE::DeviceQueueCreateInfo * pQueueCreateInfos_ = {},
                                           uint32_t                                            enabledLayerCount_ = {},
                                           const char * const * ppEnabledLayerNames_                              = {},
                                           uint32_t             enabledExtensionCount_                            = {},
                                           const char * const * ppEnabledExtensionNames_                          = {},
                                           const VULKAN_HPP_NAMESPACE::PhysicalDeviceFeatures * pEnabledFeatures_ = {} )
		*/
		std::vector<const char*> enabledLayers;
		if (debug) {
			enabledLayers.push_back("VK_LAYER_KHRONOS_validation");
		}
		vk::DeviceCreateInfo deviceInfo = vk::DeviceCreateInfo(
			vk::DeviceCreateFlags(), 
			queueCreateInfo.size(), queueCreateInfo.data(),
			enabledLayers.size(), enabledLayers.data(),
			deviceExtensions.size(), deviceExtensions.data(),
			&deviceFeatures
		);

		try {
			vk::Device device = physicalDevice.createDevice(deviceInfo);
			if (debug) {
				std::cout << "GPU has been successfully abstracted!\n";
			}
			return device;
		}
		catch (vk::SystemError err) {
			if (debug) {
				std::cout << "Device creation failed!\n";
				return nullptr;
			}
		}
		return nullptr;
	}

	/**
		Get the queues associated with the physical device.

		\param physicalDevice the physical device
		\param device the logical device
		\param debug whether the system is running in debug mode
		\returns the queues
	*/
	std::array<vk::Queue,2> get_queues(vk::PhysicalDevice physicalDevice, vk::Device device, vk::SurfaceKHR surface, bool debug) {

		QueueFamilyIndices indices = findQueueFamilies(physicalDevice, surface, debug);

		return { {
				device.getQueue(indices.graphicsFamily.value(), 0),
				device.getQueue(indices.presentFamily.value(), 0),
			} };
	}

	/**
		Check the supported swapchain parameters

		\param device the physical device
		\param surface the window surface which will use the swapchain
		\param debug whether the system is running in debug mode
		\returns a struct holding the details
	*/
	SwapChainSupportDetails query_swapchain_support(vk::PhysicalDevice device, vk::SurfaceKHR surface, bool debug) {
		SwapChainSupportDetails support;

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
		support.capabilities = device.getSurfaceCapabilitiesKHR(surface);
		if (debug) {
			std::cout << "Swapchain can support the following surface capabilities:\n";

			std::cout << "\tminimum image count: " << support.capabilities.minImageCount << '\n';
			std::cout << "\tmaximum image count: " << support.capabilities.maxImageCount << '\n';

			std::cout << "\tcurrent extent: \n";
			/*typedef struct VkExtent2D {
				uint32_t    width;
				uint32_t    height;
			} VkExtent2D;
			*/
			std::cout << "\t\twidth: " << support.capabilities.currentExtent.width << '\n';
			std::cout << "\t\theight: " << support.capabilities.currentExtent.height << '\n';

			std::cout << "\tminimum supported extent: \n";
			std::cout << "\t\twidth: " << support.capabilities.minImageExtent.width << '\n';
			std::cout << "\t\theight: " << support.capabilities.minImageExtent.height << '\n';

			std::cout << "\tmaximum supported extent: \n";
			std::cout << "\t\twidth: " << support.capabilities.maxImageExtent.width << '\n';
			std::cout << "\t\theight: " << support.capabilities.maxImageExtent.height << '\n';

			std::cout << "\tmaximum image array layers: " << support.capabilities.maxImageArrayLayers << '\n';

			
			std::cout << "\tsupported transforms:\n";
			std::vector<std::string> stringList = log_transform_bits(support.capabilities.supportedTransforms);
			for (std::string line : stringList) {
				std::cout << "\t\t" << line << '\n';
			}

			std::cout << "\tcurrent transform:\n";
			stringList = log_transform_bits(support.capabilities.currentTransform);
			for (std::string line : stringList) {
				std::cout << "\t\t" << line << '\n';
			}

			std::cout << "\tsupported alpha operations:\n";
			stringList = log_alpha_composite_bits(support.capabilities.supportedCompositeAlpha);
			for (std::string line : stringList) {
				std::cout << "\t\t" << line << '\n';
			}

			std::cout << "\tsupported image usage:\n";
			stringList = log_image_usage_bits(support.capabilities.supportedUsageFlags);
			for (std::string line : stringList) {
				std::cout << "\t\t" << line << '\n';
			}
		}

		support.formats = device.getSurfaceFormatsKHR(surface);

		if (debug) {

			for (vk::SurfaceFormatKHR supportedFormat : support.formats) {
				/*
				* typedef struct VkSurfaceFormatKHR {
					VkFormat           format;
					VkColorSpaceKHR    colorSpace;
				} VkSurfaceFormatKHR;
				*/

				std::cout << "supported pixel format: " << vk::to_string(supportedFormat.format) << '\n';
				std::cout << "supported color space: " << vk::to_string(supportedFormat.colorSpace) << '\n';
			}
		}

		support.presentModes = device.getSurfacePresentModesKHR(surface);

		for (vk::PresentModeKHR presentMode : support.presentModes) {
			std::cout << '\t' << log_present_mode(presentMode) << '\n';
		}
		return support;
	}

	/**
		Choose a surface format for the swapchain

		\param formats a vector of surface formats supported by the device
		\returns the chosen format
	*/
	vk::SurfaceFormatKHR choose_swapchain_surface_format(std::vector<vk::SurfaceFormatKHR> formats) {

		for (vk::SurfaceFormatKHR format : formats) {
			if (format.format == vk::Format::eB8G8R8A8Unorm
				&& format.colorSpace == vk::ColorSpaceKHR::eSrgbNonlinear) {
				return format;
			}
		}

		return formats[0];
	}

	/**
		Choose a present mode.

		\param presentModes a vector of present modes supported by the device
		\returns the chosen present mode
	*/
	vk::PresentModeKHR choose_swapchain_present_mode(std::vector<vk::PresentModeKHR> presentModes) {
		
		for (vk::PresentModeKHR presentMode : presentModes) {
			if (presentMode == vk::PresentModeKHR::eMailbox) {
				return presentMode;
			}
		}

		return vk::PresentModeKHR::eFifo;
	}

	/**
		Choose an extent for the swapchain.

		\param width the requested width
		\param height the requested height
		\param capabilities a struct describing the supported capabilities of the device
		\returns the chosen extent
	*/
	vk::Extent2D choose_swapchain_extent(uint32_t width, uint32_t height, vk::SurfaceCapabilitiesKHR capabilities) {

		if (capabilities.currentExtent.width != UINT32_MAX) {
			return capabilities.currentExtent;
		}
		else {
			vk::Extent2D extent = { width, height };

			extent.width = std::min(
				capabilities.maxImageExtent.width, 
				std::max(capabilities.minImageExtent.width, extent.width)
			);

			extent.height = std::min(
				capabilities.maxImageExtent.height,
				std::max(capabilities.minImageExtent.height, extent.height)
			);

			return extent;
		}
	}

	/**
		Create a swapchain

		\param logicalDevice the logical device
		\param physicalDevice the physical device
		\param surface the window surface to use the swapchain with
		\param width the requested width
		\param height the requested height
		\param debug whether the system is running in debug mode
		\returns a struct holding the swapchain and other associated data structures
	*/
	SwapChainBundle create_swapchain(vk::Device logicalDevice, vk::PhysicalDevice physicalDevice, vk::SurfaceKHR surface, int width, int height, bool debug) {

		SwapChainSupportDetails support = query_swapchain_support(physicalDevice, surface, debug);

		vk::SurfaceFormatKHR format = choose_swapchain_surface_format(support.formats);

		vk::PresentModeKHR presentMode = choose_swapchain_present_mode(support.presentModes);

		vk::Extent2D extent = choose_swapchain_extent(width, height, support.capabilities);

		uint32_t imageCount = std::min(
			support.capabilities.maxImageCount,
			support.capabilities.minImageCount + 1
		);

		/*
		* VULKAN_HPP_CONSTEXPR SwapchainCreateInfoKHR(
      VULKAN_HPP_NAMESPACE::SwapchainCreateFlagsKHR flags_         = {},
      VULKAN_HPP_NAMESPACE::SurfaceKHR              surface_       = {},
      uint32_t                                      minImageCount_ = {},
      VULKAN_HPP_NAMESPACE::Format                  imageFormat_   = VULKAN_HPP_NAMESPACE::Format::eUndefined,
      VULKAN_HPP_NAMESPACE::ColorSpaceKHR   imageColorSpace_  = VULKAN_HPP_NAMESPACE::ColorSpaceKHR::eSrgbNonlinear,
      VULKAN_HPP_NAMESPACE::Extent2D        imageExtent_      = {},
      uint32_t                              imageArrayLayers_ = {},
      VULKAN_HPP_NAMESPACE::ImageUsageFlags imageUsage_       = {},
      VULKAN_HPP_NAMESPACE::SharingMode     imageSharingMode_ = VULKAN_HPP_NAMESPACE::SharingMode::eExclusive,
      uint32_t                              queueFamilyIndexCount_ = {},
      const uint32_t *                      pQueueFamilyIndices_   = {},
      VULKAN_HPP_NAMESPACE::SurfaceTransformFlagBitsKHR preTransform_ =
        VULKAN_HPP_NAMESPACE::SurfaceTransformFlagBitsKHR::eIdentity,
      VULKAN_HPP_NAMESPACE::CompositeAlphaFlagBitsKHR compositeAlpha_ =
        VULKAN_HPP_NAMESPACE::CompositeAlphaFlagBitsKHR::eOpaque,
      VULKAN_HPP_NAMESPACE::PresentModeKHR presentMode_  = VULKAN_HPP_NAMESPACE::PresentModeKHR::eImmediate,
      VULKAN_HPP_NAMESPACE::Bool32         clipped_      = {},
      VULKAN_HPP_NAMESPACE::SwapchainKHR   oldSwapchain_ = {} ) VULKAN_HPP_NOEXCEPT
		*/
		vk::SwapchainCreateInfoKHR createInfo = vk::SwapchainCreateInfoKHR(
			vk::SwapchainCreateFlagsKHR(), surface, imageCount, format.format, format.colorSpace,
			extent, 1, vk::ImageUsageFlagBits::eColorAttachment
		);


		QueueFamilyIndices indices = findQueueFamilies(physicalDevice, surface, debug);
		uint32_t queueFamilyIndices[] = { indices.graphicsFamily.value(), indices.presentFamily.value() };

		if (indices.graphicsFamily != indices.presentFamily) {
			createInfo.imageSharingMode = vk::SharingMode::eConcurrent;
			createInfo.queueFamilyIndexCount = 2;
			createInfo.pQueueFamilyIndices = queueFamilyIndices;
		}
		else {
			createInfo.imageSharingMode = vk::SharingMode::eExclusive;
		}

		createInfo.preTransform = support.capabilities.currentTransform;
		createInfo.compositeAlpha = vk::CompositeAlphaFlagBitsKHR::eOpaque;
		createInfo.presentMode = presentMode;
		createInfo.clipped = VK_TRUE;

		createInfo.oldSwapchain = vk::SwapchainKHR(nullptr);

		SwapChainBundle bundle{};
		try {
			bundle.swapchain = logicalDevice.createSwapchainKHR(createInfo);
		}
		catch (vk::SystemError err) {
			throw std::runtime_error("failed to create swap chain!");
		}

		bundle.images = logicalDevice.getSwapchainImagesKHR(bundle.swapchain);
		bundle.format = format.format;
		bundle.extent = extent;

		return bundle;
	}
}