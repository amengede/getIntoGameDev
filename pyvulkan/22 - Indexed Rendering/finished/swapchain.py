from config import *
import vklogging
import queue_families
import frame
import image

class SwapChainSupportDetails:


    def __init__(self):
        
        self.capabilities = None
        self.formats = None
        self.presentModes = None

class SwapChainBundle:


    def __init__(self):
        
        self.swapchain = None
        self.frames = []
        self.format = None
        self.extent = None

def query_swapchain_support(instance, physicalDevice, surface):

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
    vkGetPhysicalDeviceSurfaceCapabilitiesKHR = vkGetInstanceProcAddr(
        instance, 'vkGetPhysicalDeviceSurfaceCapabilitiesKHR'
    )
    support.capabilities = vkGetPhysicalDeviceSurfaceCapabilitiesKHR(physicalDevice, surface)
    
    vklogging.logger.log_surface_capabilities(support)

    vkGetPhysicalDeviceSurfaceFormatsKHR = vkGetInstanceProcAddr(
        instance, 'vkGetPhysicalDeviceSurfaceFormatsKHR'
    )
    support.formats = vkGetPhysicalDeviceSurfaceFormatsKHR(physicalDevice, surface)

    for supportedFormat in support.formats:
        vklogging.logger.log_surface_format(supportedFormat)

    vkGetPhysicalDeviceSurfacePresentModesKHR = vkGetInstanceProcAddr(
        instance, 'vkGetPhysicalDeviceSurfacePresentModesKHR'
    )
    support.presentModes = vkGetPhysicalDeviceSurfacePresentModesKHR(physicalDevice, surface)

    vklogging.logger.log_list(support.presentModes)

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

def create_swapchain(instance, logicalDevice, physicalDevice, surface, width, height):

    support = query_swapchain_support(instance, physicalDevice, surface)

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

    indices = queue_families.find_queue_families(physicalDevice, instance, surface)
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

    images = vkGetSwapchainImagesKHR(logicalDevice, bundle.swapchain)

    for _image in images:

        swapchain_frame = frame.SwapChainFrame()
        swapchain_frame.image = _image
        swapchain_frame.image_view = image.make_image_view(
            logicalDevice, _image, format.format
        )
        bundle.frames.append(swapchain_frame)
    
    bundle.format = format.format
    bundle.extent = extent

    return bundle