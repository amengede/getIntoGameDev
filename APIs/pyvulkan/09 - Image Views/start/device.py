from config import *
import logging

"""
    Vulkan separates the concept of physical and logical devices. 

    A physical device usually represents a single complete implementation of Vulkan 
    (excluding instance-level functionality) available to the host, 
    of which there are a finite number. 
  
    A logical device represents an instance of that implementation 
    with its own state and resources independent of other logical devices.
"""

class QueueFamilyIndices:


    def __init__(self):

        self.graphicsFamily = None
        self.presentFamily = None
    
    def is_complete(self):

        return not(self.graphicsFamily is None or self.presentFamily is None)

class SwapChainSupportDetails:


    def __init__(self):
        
        self.capabilities = None
        self.formats = None
        self.presentModes = None

class SwapChainBundle:


    def __init__(self):
        
        self.swapchain = None
        self.images = None
        self.format = None
        self.extent = None

def check_device_extension_support(device, requestedExtensions, debug):

    """
        Check if a given physical device can satisfy a list of requested device extensions.
    """

    supportedExtensions = [
        extension.extensionName 
        for extension in vkEnumerateDeviceExtensionProperties(device, None)
    ]

    if debug:
        print("Device can support extensions:")

        for extension in supportedExtensions:
            print(f"\t\"{extension}\"")

    for extension in requestedExtensions:
        if extension not in supportedExtensions:
            return False
    
    return True

def is_suitable(device, debug):

    if debug:
        print("Checking if device is suitable")

    """
        A device is suitable if it can present to the screen, ie support
        the swapchain extension
    """
    requestedExtensions = [
        VK_KHR_SWAPCHAIN_EXTENSION_NAME
    ]

    if debug:
        print("We are requesting device extensions:")

        for extension in requestedExtensions:
            print(f"\t\"{extension}\"")

    if check_device_extension_support(device, requestedExtensions, debug):

        if debug:
            print("Device can support the requested extensions!")
        return True
    
    if debug:
        print("Device can't support the requested extensions!")

    return False

def choose_physical_device(instance, debug):

    """
        Choose a suitable physical device from a list of candidates.
    
        Note: Physical devices are neither created nor destroyed, they exist
        independently to the program.
    """

    if debug:
        print("Choosing Physical Device")

    """
        vkEnumeratePhysicalDevices(instance) -> List(vkPhysicalDevice)
    """
    availableDevices = vkEnumeratePhysicalDevices(instance)

    if debug:
        print(f"There are {len(availableDevices)} physical devices available on this system")

    # check if a suitable device can be found
    for device in availableDevices:
        if debug:
            logging.log_device_properties(device)
        if is_suitable(device, debug):
            return device

    return None

def find_queue_families(device, instance, surface, debug):
        
    indices = QueueFamilyIndices()

    surfaceSupport = vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceSurfaceSupportKHR")

    queueFamilies = vkGetPhysicalDeviceQueueFamilyProperties(device)

    if debug:
        print(f"There are {len(queueFamilies)} queue families available on the system.")

    for i,queueFamily in enumerate(queueFamilies):

        """
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
        
            * // Provided by VK_VERSION_1_0
                typedef enum VkQueueFlagBits {
                VK_QUEUE_GRAPHICS_BIT = 0x00000001,
                VK_QUEUE_COMPUTE_BIT = 0x00000002,
                VK_QUEUE_TRANSFER_BIT = 0x00000004,
                VK_QUEUE_SPARSE_BINDING_BIT = 0x00000008,
                } VkQueueFlagBits;
        """

        if queueFamily.queueFlags & VK_QUEUE_GRAPHICS_BIT:
            indices.graphicsFamily = i

            if debug:
                print(f"Queue Family {i} is suitable for graphics")
        
        if surfaceSupport(device, i, surface):
            indices.presentFamily = i

            if debug:
                print(f"Queue Family {i} is suitable for presenting")

        if indices.is_complete():
            break

    return indices

def create_logical_device(physicalDevice, instance, surface, debug):

    """
        Create an abstraction around the GPU
    """

    """
        At time of creation, any required queues will also be created,
        so queue create info must be passed in
    """
    indices = find_queue_families(physicalDevice, instance, surface, debug)
    uniqueIndices = [indices.graphicsFamily,]
    if indices.graphicsFamily != indices.presentFamily:
        uniqueIndices.append(indices.presentFamily)
    
    queueCreateInfo = []
    for queueFamilyIndex in uniqueIndices:
        queueCreateInfo.append(
            VkDeviceQueueCreateInfo(
                queueFamilyIndex = queueFamilyIndex,
                queueCount = 1,
                pQueuePriorities = [1.0,]
            )
        )

    """
        Device features must be requested before the device is abstracted,
        therefore we only pay for what we use
    """
    deviceFeatures = VkPhysicalDeviceFeatures()

    enabledLayers = []
    if debug:
        enabledLayers.append("VK_LAYER_KHRONOS_validation")
    
    deviceExtensions = [
        VK_KHR_SWAPCHAIN_EXTENSION_NAME,
    ]

    createInfo = VkDeviceCreateInfo(
        queueCreateInfoCount = len(queueCreateInfo),
        pQueueCreateInfos = queueCreateInfo,
        enabledExtensionCount = len(deviceExtensions),
        ppEnabledExtensionNames = deviceExtensions,
        pEnabledFeatures = [deviceFeatures,],
        enabledLayerCount = len(enabledLayers),
        ppEnabledLayerNames = enabledLayers
    )

    return vkCreateDevice(
        physicalDevice = physicalDevice, pCreateInfo = [createInfo,], pAllocator = None
    )

def get_queues(physicalDevice, logicalDevice, instance, surface, debug):

    indices = find_queue_families(physicalDevice, instance, surface, debug)
    return [
        vkGetDeviceQueue(
            device = logicalDevice,
            queueFamilyIndex = indices.graphicsFamily,
            queueIndex = 0
        ),
        vkGetDeviceQueue(
            device = logicalDevice,
            queueFamilyIndex = indices.presentFamily,
            queueIndex = 0
        ),
    ]

def query_swapchain_support(instance, physicalDevice, surface, debug):

    """
    typedef struct VkSurfaceCapabilitiesKHR {
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
    """
    
    support = SwapChainSupportDetails()
    vkGetPhysicalDeviceSurfaceCapabilitiesKHR = vkGetInstanceProcAddr(instance, 'vkGetPhysicalDeviceSurfaceCapabilitiesKHR')
    support.capabilities = vkGetPhysicalDeviceSurfaceCapabilitiesKHR(physicalDevice, surface)
    
    if debug:
            
        print("Swapchain can support the following surface capabilities:")

        print(f"\tminimum image count: {support.capabilities.minImageCount}")
        print(f"\tmaximum image count: {support.capabilities.maxImageCount}")

        print("\tcurrent extent:")
        """
        typedef struct VkExtent2D {
            uint32_t    width;
            uint32_t    height;
        } VkExtent2D;
        """
        print(f"\t\twidth: {support.capabilities.currentExtent.width}")
        print(f"\t\theight: {support.capabilities.currentExtent.height}")

        print("\tminimum supported extent:")
        print(f"\t\twidth: {support.capabilities.minImageExtent.width}")
        print(f"\t\theight: {support.capabilities.minImageExtent.height}")

        print("\tmaximum supported extent:")
        print(f"\t\twidth: {support.capabilities.maxImageExtent.width}")
        print(f"\t\theight: {support.capabilities.maxImageExtent.height}")

        print(f"\tmaximum image array layers: {support.capabilities.maxImageArrayLayers}")

            
        print("\tsupported transforms:")
        stringList = logging.log_transform_bits(support.capabilities.supportedTransforms)
        for line in stringList:
            print(f"\t\t{line}")

        print("\tcurrent transform:")
        stringList = logging.log_transform_bits(support.capabilities.currentTransform)
        for line in stringList:
            print(f"\t\t{line}")

        print("\tsupported alpha operations:")
        stringList = logging.log_alpha_composite_bits(support.capabilities.supportedCompositeAlpha)
        for line in stringList:
            print(f"\t\t{line}")

        print("\tsupported image usage:")
        stringList = logging.log_image_usage_bits(support.capabilities.supportedUsageFlags)
        for line in stringList:
            print(f"\t\t{line}")

    vkGetPhysicalDeviceSurfaceFormatsKHR = vkGetInstanceProcAddr(instance, 'vkGetPhysicalDeviceSurfaceFormatsKHR')
    support.formats = vkGetPhysicalDeviceSurfaceFormatsKHR(physicalDevice, surface)

    if debug:

        for supportedFormat in support.formats:
            """
            * typedef struct VkSurfaceFormatKHR {
                VkFormat           format;
                VkColorSpaceKHR    colorSpace;
            } VkSurfaceFormatKHR;
            """

            print(f"supported pixel format: {logging.format_to_string(supportedFormat.format)}")
            print(f"supported color space: {logging.colorspace_to_string(supportedFormat.colorSpace)}")

    vkGetPhysicalDeviceSurfacePresentModesKHR = vkGetInstanceProcAddr(instance, 'vkGetPhysicalDeviceSurfacePresentModesKHR')
    support.presentModes = vkGetPhysicalDeviceSurfacePresentModesKHR(physicalDevice, surface)

    for presentMode in support.presentModes:
        print(f"\t{logging.log_present_mode(presentMode)}")

    return support

def choose_swapchain_surface_format(formats):

    for format in formats:
        if (format.format == VK_FORMAT_B8G8R8A8_UNORM
            and format.colorSpace == VK_COLOR_SPACE_SRGB_NONLINEAR_KHR):
            return format

    return formats[0]

def choose_swapchain_present_mode(presentModes):
        
    for presentMode in presentModes:
        if presentMode == VK_PRESENT_MODE_MAILBOX_KHR:
            return presentMode

    return VK_PRESENT_MODE_FIFO_KHR

def choose_swapchain_extent(width, height, capabilities):
    
    extent = VkExtent2D(width, height)

    extent.width = min(
        capabilities.maxImageExtent.width, 
        max(capabilities.minImageExtent.width, extent.width)
    )

    extent.height = min(
        capabilities.maxImageExtent.height,
        max(capabilities.minImageExtent.height, extent.height)
    )

    return extent

def create_swapchain(instance, logicalDevice, physicalDevice, surface, width, height, debug):

    support = query_swapchain_support(instance, physicalDevice, surface, debug)

    format = choose_swapchain_surface_format(support.formats)

    presentMode = choose_swapchain_present_mode(support.presentModes)

    extent = choose_swapchain_extent(width, height, support.capabilities)

    imageCount = min(
        support.capabilities.maxImageCount,
        support.capabilities.minImageCount + 1
    )

    """
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
            VULKAN_HPP_NAMESPACE::SwapchainKHR   oldSwapchain_ = {} 
        ) VULKAN_HPP_NOEXCEPT
    """

    indices = find_queue_families(physicalDevice, instance, surface, debug)
    queueFamilyIndices = [
        indices.graphicsFamily, indices.presentFamily
    ]
    if (indices.graphicsFamily != indices.presentFamily):
        imageSharingMode = VK_SHARING_MODE_CONCURRENT
        queueFamilyIndexCount = 2
        pQueueFamilyIndices = queueFamilyIndices
    else:
        imageSharingMode = VK_SHARING_MODE_EXCLUSIVE
        queueFamilyIndexCount = 0
        pQueueFamilyIndices = None

    createInfo = VkSwapchainCreateInfoKHR(
        surface = surface, minImageCount = imageCount, imageFormat = format.format,
        imageColorSpace = format.colorSpace, imageExtent = extent, imageArrayLayers = 1,
        imageUsage = VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT, imageSharingMode = imageSharingMode,
        queueFamilyIndexCount = queueFamilyIndexCount, pQueueFamilyIndices = pQueueFamilyIndices,
        preTransform = support.capabilities.currentTransform, compositeAlpha = VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR,
        presentMode = presentMode, clipped = VK_TRUE
    )

    bundle = SwapChainBundle()

    vkCreateSwapchainKHR = vkGetDeviceProcAddr(logicalDevice, 'vkCreateSwapchainKHR')
    bundle.swapchain = vkCreateSwapchainKHR(logicalDevice, createInfo, None)
    vkGetSwapchainImagesKHR = vkGetDeviceProcAddr(logicalDevice, 'vkGetSwapchainImagesKHR')
    bundle.images = vkGetSwapchainImagesKHR(logicalDevice, bundle.swapchain)
    bundle.format = format.format
    bundle.extent = extent

    return bundle