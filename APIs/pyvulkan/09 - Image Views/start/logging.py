from config import *

"""
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

"""
def debugCallback(*args):
    """
    print(f"Debug messenger has {len(args)} components")
    for arg in args:
        print(f"\t{arg}")
    """
    print(f"Validation Layer: {args[5]} {args[6]}")
    return 0

def make_debug_messenger(instance):

    """
        VkDebugReportCallbackCreateInfoEXT(
            sType=VK_STRUCTURE_TYPE_DEBUG_REPORT_CALLBACK_CREATE_INFO_EXT,
            pNext=None,
            flags=None,
            pfnCallback=None,
            pUserData=None,
        )
    """

    createInfo = VkDebugReportCallbackCreateInfoEXT(
        flags=VK_DEBUG_REPORT_ERROR_BIT_EXT | VK_DEBUG_REPORT_WARNING_BIT_EXT,
        pfnCallback=debugCallback
    )

    #fetch creation function
    creationFunction = vkGetInstanceProcAddr(instance, 'vkCreateDebugReportCallbackEXT')

    """
        def vkCreateDebugReportCallbackEXT(
            instance
            ,pCreateInfo
            ,pAllocator
            ,pCallback=None
            ,):
    """
    return creationFunction(instance, createInfo, None)

def log_device_properties(device):
    
    """
        void vkGetPhysicalDeviceProperties(
            VkPhysicalDevice                            physicalDevice,
            VkPhysicalDeviceProperties*                 pProperties);

    """

    properties = vkGetPhysicalDeviceProperties(device)

    """
        typedef struct VkPhysicalDeviceProperties {
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
    """

    print(f"Device name: {properties.deviceName}")

    print("Device type: ",end="")

    if properties.deviceType == VK_PHYSICAL_DEVICE_TYPE_CPU:
        print("CPU")
    elif properties.deviceType == VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU:
        print("Discrete GPU")
    elif properties.deviceType == VK_PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU:
        print("Integrated GPU")
    elif properties.deviceType == VK_PHYSICAL_DEVICE_TYPE_VIRTUAL_GPU:
        print("Virtual GPU")
    else:
        print("Other")

def log_transform_bits(bits):

    result = []

    """
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
    """
    if (bits & VK_SURFACE_TRANSFORM_IDENTITY_BIT_KHR):
        result.append("identity")
    if (bits & VK_SURFACE_TRANSFORM_ROTATE_90_BIT_KHR):
        result.append("90 degree rotation")
    if (bits & VK_SURFACE_TRANSFORM_ROTATE_180_BIT_KHR):
        result.append("180 degree rotation")
    if (bits & VK_SURFACE_TRANSFORM_ROTATE_270_BIT_KHR):
        result.append("270 degree rotation")
    if (bits & VK_SURFACE_TRANSFORM_HORIZONTAL_MIRROR_BIT_KHR):
        result.append("horizontal mirror")
    if (bits & VK_SURFACE_TRANSFORM_HORIZONTAL_MIRROR_ROTATE_90_BIT_KHR):
        result.append("horizontal mirror, then 90 degree rotation")
    if (bits & VK_SURFACE_TRANSFORM_HORIZONTAL_MIRROR_ROTATE_180_BIT_KHR):
        result.append("horizontal mirror, then 180 degree rotation")
    if (bits & VK_SURFACE_TRANSFORM_HORIZONTAL_MIRROR_ROTATE_270_BIT_KHR):
        result.append("horizontal mirror, then 270 degree rotation")
    if (bits & VK_SURFACE_TRANSFORM_INHERIT_BIT_KHR):
        result.append("inherited")

    return result


def log_alpha_composite_bits(bits):
    
    result = []

    """
    typedef enum VkCompositeAlphaFlagBitsKHR {
        VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR = 0x00000001,
        VK_COMPOSITE_ALPHA_PRE_MULTIPLIED_BIT_KHR = 0x00000002,
        VK_COMPOSITE_ALPHA_POST_MULTIPLIED_BIT_KHR = 0x00000004,
        VK_COMPOSITE_ALPHA_INHERIT_BIT_KHR = 0x00000008,
    } VkCompositeAlphaFlagBitsKHR;
    """

    if (bits & VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR):
        result.append("opaque (alpha ignored)")
    if (bits & VK_COMPOSITE_ALPHA_PRE_MULTIPLIED_BIT_KHR):
        result.append("pre multiplied (alpha expected to already be multiplied in image)")
    if (bits & VK_COMPOSITE_ALPHA_POST_MULTIPLIED_BIT_KHR):
        result.append("post multiplied (alpha will be applied during composition)")
    if (bits & VK_COMPOSITE_ALPHA_INHERIT_BIT_KHR):
        result.append("inherited")

    return result

def log_image_usage_bits(bits):

    result = []

    """
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
    """

    if (bits & VK_IMAGE_USAGE_TRANSFER_SRC_BIT):
        result.append("transfer src: image can be used as the source of a transfer command.")
    if (bits & VK_IMAGE_USAGE_TRANSFER_DST_BIT):
        result.append("transfer dst: image can be used as the destination of a transfer command.")
    if (bits & VK_IMAGE_USAGE_SAMPLED_BIT):
        result.append("""sampled: image can be used to create a VkImageView suitable for occupying a 
VkDescriptorSet slot either of type VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE or 
VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER, and be sampled by a shader.""")
    if (bits & VK_IMAGE_USAGE_STORAGE_BIT):
        result.append("""storage: image can be used to create a VkImageView suitable for occupying a 
VkDescriptorSet slot of type VK_DESCRIPTOR_TYPE_STORAGE_IMAGE.""")
    if (bits & VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT):
        result.append("""color attachment: image can be used to create a VkImageView suitable for use as 
a color or resolve attachment in a VkFramebuffer.""")
    if (bits & VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT):
        result.append("""depth/stencil attachment: image can be used to create a VkImageView 
suitable for use as a depth/stencil or depth/stencil resolve attachment in a VkFramebuffer.""")
    if (bits & VK_IMAGE_USAGE_TRANSIENT_ATTACHMENT_BIT ):
        result.append("""transient attachment: implementations may support using memory allocations 
with the VK_MEMORY_PROPERTY_LAZILY_ALLOCATED_BIT to back an image with this usage. This 
bit can be set for any image that can be used to create a VkImageView suitable for use as 
a color, resolve, depth/stencil, or input attachment.""")
    if (bits & VK_IMAGE_USAGE_INPUT_ATTACHMENT_BIT):
        result.append("""input attachment: image can be used to create a VkImageView suitable for 
occupying VkDescriptorSet slot of type VK_DESCRIPTOR_TYPE_INPUT_ATTACHMENT; be read from 
a shader as an input attachment; and be used as an input attachment in a framebuffer.""")
    if (bits & VK_IMAGE_USAGE_FRAGMENT_DENSITY_MAP_BIT_EXT):
        result.append("""fragment density map: image can be used to create a VkImageView suitable 
for use as a fragment density map image.""")

    return result

def log_present_mode(presentMode):
    
    """
    * // Provided by VK_KHR_surface
    typedef enum VkPresentModeKHR {
        VK_PRESENT_MODE_IMMEDIATE_KHR = 0,
        VK_PRESENT_MODE_MAILBOX_KHR = 1,
        VK_PRESENT_MODE_FIFO_KHR = 2,
        VK_PRESENT_MODE_FIFO_RELAXED_KHR = 3,
        // Provided by VK_KHR_shared_presentable_image
        VK_PRESENT_MODE_SHARED_DEMAND_REFRESH_KHR = 1000111000,
        // Provided by VK_KHR_shared_presentable_image
        VK_PRESENT_MODE_SHARED_CONTINUOUS_REFRESH_KHR = 1000111001,
    } VkPresentModeKHR;
    """

    if (presentMode == VK_PRESENT_MODE_IMMEDIATE_KHR):
        return """immediate: the presentation engine does not wait for a vertical blanking period 
to update the current image, meaning this mode may result in visible tearing. No internal 
queuing of presentation requests is needed, as the requests are applied immediately."""
    if (presentMode == VK_PRESENT_MODE_MAILBOX_KHR):
        return """mailbox: the presentation engine waits for the next vertical blanking period 
to update the current image. Tearing cannot be observed. An internal single-entry queue is 
used to hold pending presentation requests. If the queue is full when a new presentation 
request is received, the new request replaces the existing entry, and any images associated 
with the prior entry become available for re-use by the application. One request is removed 
from the queue and processed during each vertical blanking period in which the queue is non-empty."""
    if (presentMode == VK_PRESENT_MODE_FIFO_KHR):
        return """fifo: the presentation engine waits for the next vertical blanking 
period to update the current image. Tearing cannot be observed. An internal queue is used to 
hold pending presentation requests. New requests are appended to the end of the queue, and one 
request is removed from the beginning of the queue and processed during each vertical blanking 
period in which the queue is non-empty. This is the only value of presentMode that is required 
to be supported."""
    if (presentMode == VK_PRESENT_MODE_FIFO_RELAXED_KHR):
        return """relaxed fifo: the presentation engine generally waits for the next vertical 
blanking period to update the current image. If a vertical blanking period has already passed 
since the last update of the current image then the presentation engine does not wait for 
another vertical blanking period for the update, meaning this mode may result in visible tearing 
in this case. This mode is useful for reducing visual stutter with an application that will 
mostly present a new image before the next vertical blanking period, but may occasionally be 
late, and present a new image just after the next vertical blanking period. An internal queue 
is used to hold pending presentation requests. New requests are appended to the end of the queue, 
and one request is removed from the beginning of the queue and processed during or after each 
vertical blanking period in which the queue is non-empty."""
    if (presentMode == VK_PRESENT_MODE_SHARED_DEMAND_REFRESH_KHR):
        return """shared demand refresh: the presentation engine and application have 
concurrent access to a single image, which is referred to as a shared presentable image. 
The presentation engine is only required to update the current image after a new presentation 
request is received. Therefore the application must make a presentation request whenever an 
update is required. However, the presentation engine may update the current image at any point, 
meaning this mode may result in visible tearing."""
    if (presentMode == VK_PRESENT_MODE_SHARED_CONTINUOUS_REFRESH_KHR):
        return """shared continuous refresh: the presentation engine and application have 
concurrent access to a single image, which is referred to as a shared presentable image. The 
presentation engine periodically updates the current image on its regular refresh cycle. The 
application is only required to make one initial presentation request, after which the 
presentation engine must update the current image without any need for further presentation 
requests. The application can indicate the image contents have been updated by making a 
presentation request, but this does not guarantee the timing of when it will be updated. 
This mode may result in visible tearing if rendering to the image is not timed correctly."""

    return "none/undefined"

def format_to_string(format):

    format_lookup = {
        VK_FORMAT_UNDEFINED: "VK_FORMAT_UNDEFINED", VK_FORMAT_R4G4_UNORM_PACK8: "VK_FORMAT_R4G4_UNORM_PACK8",
        VK_FORMAT_R4G4B4A4_UNORM_PACK16: "VK_FORMAT_R4G4B4A4_UNORM_PACK16", VK_FORMAT_B4G4R4A4_UNORM_PACK16 : "VK_FORMAT_B4G4R4A4_UNORM_PACK16",
        VK_FORMAT_R5G6B5_UNORM_PACK16 : "VK_FORMAT_R5G6B5_UNORM_PACK16", VK_FORMAT_B5G6R5_UNORM_PACK16 : "VK_FORMAT_B5G6R5_UNORM_PACK16",
        VK_FORMAT_R5G5B5A1_UNORM_PACK16 : "VK_FORMAT_R5G5B5A1_UNORM_PACK16", VK_FORMAT_B5G5R5A1_UNORM_PACK16 : "VK_FORMAT_B5G5R5A1_UNORM_PACK16",
        VK_FORMAT_A1R5G5B5_UNORM_PACK16 : "VK_FORMAT_A1R5G5B5_UNORM_PACK16", VK_FORMAT_R8_UNORM : "VK_FORMAT_R8_UNORM", 
        VK_FORMAT_R8_SNORM : "VK_FORMAT_R8_SNORM", VK_FORMAT_R8_USCALED : "VK_FORMAT_R8_USCALED", 
        VK_FORMAT_R8_SSCALED : "VK_FORMAT_R8_SSCALED", VK_FORMAT_R8_UINT : "VK_FORMAT_R8_UINT", 
        VK_FORMAT_R8_SINT : "VK_FORMAT_R8_SINT", VK_FORMAT_R8_SRGB : "VK_FORMAT_R8_SRGB", 
        VK_FORMAT_R8G8_UNORM : "VK_FORMAT_R8G8_UNORM", VK_FORMAT_R8G8_SNORM : "VK_FORMAT_R8G8_SNORM", 
        VK_FORMAT_R8G8_USCALED : "VK_FORMAT_R8G8_USCALED", VK_FORMAT_R8G8_SSCALED : "VK_FORMAT_R8G8_SSCALED", 
        VK_FORMAT_R8G8_UINT : "VK_FORMAT_R8G8_UINT", VK_FORMAT_R8G8_SINT : "VK_FORMAT_R8G8_SINT", 
        VK_FORMAT_R8G8_SRGB : "VK_FORMAT_R8G8_SRGB", VK_FORMAT_R8G8B8_UNORM : "VK_FORMAT_R8G8B8_UNORM", 
        VK_FORMAT_R8G8B8_SNORM : "VK_FORMAT_R8G8B8_SNORM", VK_FORMAT_R8G8B8_USCALED : "VK_FORMAT_R8G8B8_USCALED", 
        VK_FORMAT_R8G8B8_SSCALED : "VK_FORMAT_R8G8B8_SSCALED", VK_FORMAT_R8G8B8_UINT : "VK_FORMAT_R8G8B8_UINT", 
        VK_FORMAT_R8G8B8_SINT : "VK_FORMAT_R8G8B8_SINT", VK_FORMAT_R8G8B8_SRGB : "VK_FORMAT_R8G8B8_SRGB", 
        VK_FORMAT_B8G8R8_UNORM : "VK_FORMAT_B8G8R8_UNORM", VK_FORMAT_B8G8R8_SNORM : "VK_FORMAT_B8G8R8_SNORM", 
        VK_FORMAT_B8G8R8_USCALED : "VK_FORMAT_B8G8R8_USCALED", VK_FORMAT_B8G8R8_SSCALED : "VK_FORMAT_B8G8R8_SSCALED", 
        VK_FORMAT_B8G8R8_UINT : "VK_FORMAT_B8G8R8_UINT", VK_FORMAT_B8G8R8_SINT : "VK_FORMAT_B8G8R8_SINT", 
        VK_FORMAT_B8G8R8_SRGB : "VK_FORMAT_B8G8R8_SRGB", VK_FORMAT_R8G8B8A8_UNORM : "VK_FORMAT_R8G8B8A8_UNORM", 
        VK_FORMAT_R8G8B8A8_SNORM : "VK_FORMAT_R8G8B8A8_SNORM", VK_FORMAT_R8G8B8A8_USCALED : "VK_FORMAT_R8G8B8A8_USCALED", 
        VK_FORMAT_R8G8B8A8_SSCALED : "VK_FORMAT_R8G8B8A8_SSCALED", VK_FORMAT_R8G8B8A8_UINT : "VK_FORMAT_R8G8B8A8_UINT", 
        VK_FORMAT_R8G8B8A8_SINT : "VK_FORMAT_R8G8B8A8_SINT", VK_FORMAT_R8G8B8A8_SRGB : "VK_FORMAT_R8G8B8A8_SRGB", 
        VK_FORMAT_B8G8R8A8_UNORM : "VK_FORMAT_B8G8R8A8_UNORM", VK_FORMAT_B8G8R8A8_SNORM : "VK_FORMAT_B8G8R8A8_SNORM", 
        VK_FORMAT_B8G8R8A8_USCALED : "VK_FORMAT_B8G8R8A8_USCALED", VK_FORMAT_B8G8R8A8_SSCALED : "VK_FORMAT_B8G8R8A8_SSCALED", 
        VK_FORMAT_B8G8R8A8_UINT : "VK_FORMAT_B8G8R8A8_UINT", VK_FORMAT_B8G8R8A8_SINT : "VK_FORMAT_B8G8R8A8_SINT",
        VK_FORMAT_B8G8R8A8_SRGB : "VK_FORMAT_B8G8R8A8_SRGB", VK_FORMAT_A8B8G8R8_UNORM_PACK32 : "VK_FORMAT_A8B8G8R8_UNORM_PACK32",
        VK_FORMAT_A8B8G8R8_SNORM_PACK32 : "VK_FORMAT_A8B8G8R8_SNORM_PACK32", VK_FORMAT_A8B8G8R8_USCALED_PACK32 : "VK_FORMAT_A8B8G8R8_USCALED_PACK32",
        VK_FORMAT_A8B8G8R8_SSCALED_PACK32 : "VK_FORMAT_A8B8G8R8_SSCALED_PACK32", VK_FORMAT_A8B8G8R8_UINT_PACK32 : "VK_FORMAT_A8B8G8R8_UINT_PACK32",
        VK_FORMAT_A8B8G8R8_SINT_PACK32 : "VK_FORMAT_A8B8G8R8_SINT_PACK32", VK_FORMAT_A8B8G8R8_SRGB_PACK32 : "VK_FORMAT_A8B8G8R8_SRGB_PACK32",
        VK_FORMAT_A2R10G10B10_UNORM_PACK32 : "VK_FORMAT_A2R10G10B10_UNORM_PACK32", VK_FORMAT_A2R10G10B10_SNORM_PACK32 : "VK_FORMAT_A2R10G10B10_SNORM_PACK32",
        VK_FORMAT_A2R10G10B10_USCALED_PACK32 : "VK_FORMAT_A2R10G10B10_USCALED_PACK32", VK_FORMAT_A2R10G10B10_SSCALED_PACK32 : "VK_FORMAT_A2R10G10B10_SSCALED_PACK32",
        VK_FORMAT_A2R10G10B10_UINT_PACK32 : "VK_FORMAT_A2R10G10B10_UINT_PACK32", VK_FORMAT_A2R10G10B10_SINT_PACK32 : "VK_FORMAT_A2R10G10B10_SINT_PACK32",
        VK_FORMAT_A2B10G10R10_UNORM_PACK32 : "VK_FORMAT_A2B10G10R10_UNORM_PACK32", VK_FORMAT_A2B10G10R10_SNORM_PACK32 : "VK_FORMAT_A2B10G10R10_SNORM_PACK32",
        VK_FORMAT_A2B10G10R10_USCALED_PACK32 : "VK_FORMAT_A2B10G10R10_USCALED_PACK32", VK_FORMAT_A2B10G10R10_SSCALED_PACK32 : "VK_FORMAT_A2B10G10R10_SSCALED_PACK32",
        VK_FORMAT_A2B10G10R10_UINT_PACK32 : "VK_FORMAT_A2B10G10R10_UINT_PACK32", VK_FORMAT_A2B10G10R10_SINT_PACK32 : "VK_FORMAT_A2B10G10R10_SINT_PACK32",
        VK_FORMAT_R16_UNORM : "VK_FORMAT_R16_UNORM", VK_FORMAT_R16_SNORM : "VK_FORMAT_R16_SNORM",
        VK_FORMAT_R16_USCALED : "VK_FORMAT_R16_USCALED", VK_FORMAT_R16_SSCALED : "VK_FORMAT_R16_SSCALED",
        VK_FORMAT_R16_UINT : "VK_FORMAT_R16_UINT", VK_FORMAT_R16_SINT : "VK_FORMAT_R16_SINT",
        VK_FORMAT_R16_SFLOAT : "VK_FORMAT_R16_SFLOAT", VK_FORMAT_R16G16_UNORM : "VK_FORMAT_R16G16_UNORM",
        VK_FORMAT_R16G16_SNORM : "VK_FORMAT_R16G16_SNORM", VK_FORMAT_R16G16_USCALED : "VK_FORMAT_R16G16_USCALED",
        VK_FORMAT_R16G16_SSCALED : "VK_FORMAT_R16G16_SSCALED", VK_FORMAT_R16G16_UINT : "VK_FORMAT_R16G16_UINT",
        VK_FORMAT_R16G16_SINT : "VK_FORMAT_R16G16_SINT", VK_FORMAT_R16G16_SFLOAT : "VK_FORMAT_R16G16_SFLOAT",
        VK_FORMAT_R16G16B16_UNORM : "VK_FORMAT_R16G16B16_UNORM", VK_FORMAT_R16G16B16_SNORM : "VK_FORMAT_R16G16B16_SNORM",
        VK_FORMAT_R16G16B16_USCALED : "VK_FORMAT_R16G16B16_USCALED", VK_FORMAT_R16G16B16_SSCALED : "VK_FORMAT_R16G16B16_SSCALED",
        VK_FORMAT_R16G16B16_UINT : "VK_FORMAT_R16G16B16_UINT", VK_FORMAT_R16G16B16_SINT : "VK_FORMAT_R16G16B16_SINT",
        VK_FORMAT_R16G16B16_SFLOAT : "VK_FORMAT_R16G16B16_SFLOAT", VK_FORMAT_R16G16B16A16_UNORM : "VK_FORMAT_R16G16B16A16_UNORM",
        VK_FORMAT_R16G16B16A16_SNORM : "VK_FORMAT_R16G16B16A16_SNORM", VK_FORMAT_R16G16B16A16_USCALED : "VK_FORMAT_R16G16B16A16_USCALED",
        VK_FORMAT_R16G16B16A16_SSCALED : "VK_FORMAT_R16G16B16A16_SSCALED", VK_FORMAT_R16G16B16A16_UINT : "VK_FORMAT_R16G16B16A16_UINT",
        VK_FORMAT_R16G16B16A16_SINT : "VK_FORMAT_R16G16B16A16_SINT", VK_FORMAT_R16G16B16A16_SFLOAT : "VK_FORMAT_R16G16B16A16_SFLOAT",
        VK_FORMAT_R32_UINT : "VK_FORMAT_R32_UINT", VK_FORMAT_R32_SINT : "VK_FORMAT_R32_SINT",
        VK_FORMAT_R32_SFLOAT : "VK_FORMAT_R32_SFLOAT", VK_FORMAT_R32G32_UINT : "VK_FORMAT_R32G32_UINT",
        VK_FORMAT_R32G32_SINT : "VK_FORMAT_R32G32_SINT", VK_FORMAT_R32G32_SFLOAT : "VK_FORMAT_R32G32_SFLOAT",
        VK_FORMAT_R32G32B32_UINT : "VK_FORMAT_R32G32B32_UINT", VK_FORMAT_R32G32B32_SINT : "VK_FORMAT_R32G32B32_SINT",
        VK_FORMAT_R32G32B32_SFLOAT : "VK_FORMAT_R32G32B32_SFLOAT", VK_FORMAT_R32G32B32A32_UINT : "VK_FORMAT_R32G32B32A32_UINT",
        VK_FORMAT_R32G32B32A32_SINT : "VK_FORMAT_R32G32B32A32_SINT", VK_FORMAT_R32G32B32A32_SFLOAT : "VK_FORMAT_R32G32B32A32_SFLOAT",
        VK_FORMAT_R64_UINT : "VK_FORMAT_R64_UINT", VK_FORMAT_R64_SINT : "VK_FORMAT_R64_SINT",
        VK_FORMAT_R64_SFLOAT : "VK_FORMAT_R64_SFLOAT", VK_FORMAT_R64G64_UINT : "VK_FORMAT_R64G64_UINT",
        VK_FORMAT_R64G64_SINT : "VK_FORMAT_R64G64_SINT", VK_FORMAT_R64G64_SFLOAT : "VK_FORMAT_R64G64_SFLOAT",
        VK_FORMAT_R64G64B64_UINT : "VK_FORMAT_R64G64B64_UINT", VK_FORMAT_R64G64B64_SINT : "VK_FORMAT_R64G64B64_SINT",
        VK_FORMAT_R64G64B64_SFLOAT : "VK_FORMAT_R64G64B64_SFLOAT", VK_FORMAT_R64G64B64A64_UINT : "VK_FORMAT_R64G64B64A64_UINT",
        VK_FORMAT_R64G64B64A64_SINT : "VK_FORMAT_R64G64B64A64_SINT", VK_FORMAT_R64G64B64A64_SFLOAT : "VK_FORMAT_R64G64B64A64_SFLOAT",
        VK_FORMAT_B10G11R11_UFLOAT_PACK32 : "VK_FORMAT_B10G11R11_UFLOAT_PACK32", VK_FORMAT_E5B9G9R9_UFLOAT_PACK32 : "VK_FORMAT_E5B9G9R9_UFLOAT_PACK32",
        VK_FORMAT_D16_UNORM : "VK_FORMAT_D16_UNORM", VK_FORMAT_X8_D24_UNORM_PACK32 : "VK_FORMAT_X8_D24_UNORM_PACK325",
        VK_FORMAT_D32_SFLOAT : "VK_FORMAT_D32_SFLOAT", VK_FORMAT_S8_UINT : "VK_FORMAT_S8_UINT",
        VK_FORMAT_D16_UNORM_S8_UINT : "VK_FORMAT_D16_UNORM_S8_UINT", VK_FORMAT_D24_UNORM_S8_UINT : "VK_FORMAT_D24_UNORM_S8_UINT",
        VK_FORMAT_D32_SFLOAT_S8_UINT : "VK_FORMAT_D32_SFLOAT_S8_UINT", VK_FORMAT_BC1_RGB_UNORM_BLOCK : "VK_FORMAT_BC1_RGB_UNORM_BLOCK",
        VK_FORMAT_BC1_RGB_SRGB_BLOCK : "VK_FORMAT_BC1_RGB_SRGB_BLOCK", VK_FORMAT_BC1_RGBA_UNORM_BLOCK : "VK_FORMAT_BC1_RGBA_UNORM_BLOCK",
        VK_FORMAT_BC1_RGBA_SRGB_BLOCK : "VK_FORMAT_BC1_RGBA_SRGB_BLOCK", VK_FORMAT_BC2_UNORM_BLOCK : "VK_FORMAT_BC2_UNORM_BLOCK",
        VK_FORMAT_BC2_SRGB_BLOCK : "VK_FORMAT_BC2_SRGB_BLOCK", VK_FORMAT_BC3_UNORM_BLOCK : "VK_FORMAT_BC3_UNORM_BLOCK",
        VK_FORMAT_BC3_SRGB_BLOCK : "VK_FORMAT_BC3_SRGB_BLOCK", VK_FORMAT_BC4_UNORM_BLOCK : "VK_FORMAT_BC4_UNORM_BLOCK",
        VK_FORMAT_BC4_SNORM_BLOCK : "VK_FORMAT_BC4_SNORM_BLOCK", VK_FORMAT_BC5_UNORM_BLOCK : "VK_FORMAT_BC5_UNORM_BLOCK",
        VK_FORMAT_BC5_SNORM_BLOCK : "VK_FORMAT_BC5_SNORM_BLOCK", VK_FORMAT_BC6H_UFLOAT_BLOCK : "VK_FORMAT_BC6H_UFLOAT_BLOCK",
        VK_FORMAT_BC6H_SFLOAT_BLOCK : "VK_FORMAT_BC6H_SFLOAT_BLOCK", VK_FORMAT_BC7_UNORM_BLOCK : "VK_FORMAT_BC7_UNORM_BLOCK",
        VK_FORMAT_BC7_SRGB_BLOCK : "VK_FORMAT_BC7_SRGB_BLOCK", VK_FORMAT_ETC2_R8G8B8_UNORM_BLOCK : "VK_FORMAT_ETC2_R8G8B8_UNORM_BLOCK",
        VK_FORMAT_ETC2_R8G8B8_SRGB_BLOCK : "VK_FORMAT_ETC2_R8G8B8_SRGB_BLOCK", VK_FORMAT_ETC2_R8G8B8A1_UNORM_BLOCK : "VK_FORMAT_ETC2_R8G8B8A1_UNORM_BLOCK",
        VK_FORMAT_ETC2_R8G8B8A1_SRGB_BLOCK : "VK_FORMAT_ETC2_R8G8B8A1_SRGB_BLOCK", VK_FORMAT_ETC2_R8G8B8A8_UNORM_BLOCK : "VK_FORMAT_ETC2_R8G8B8A8_UNORM_BLOCK",
        VK_FORMAT_ETC2_R8G8B8A8_SRGB_BLOCK : "VK_FORMAT_ETC2_R8G8B8A8_SRGB_BLOCK", VK_FORMAT_EAC_R11_UNORM_BLOCK : "VK_FORMAT_EAC_R11_UNORM_BLOCK",
        VK_FORMAT_EAC_R11_SNORM_BLOCK : "VK_FORMAT_EAC_R11_SNORM_BLOCK", VK_FORMAT_EAC_R11G11_UNORM_BLOCK : "VK_FORMAT_EAC_R11G11_UNORM_BLOCK",
        VK_FORMAT_EAC_R11G11_SNORM_BLOCK : "VK_FORMAT_EAC_R11G11_SNORM_BLOCK", VK_FORMAT_ASTC_4x4_UNORM_BLOCK : "VK_FORMAT_ASTC_4x4_UNORM_BLOCK",
        VK_FORMAT_ASTC_4x4_SRGB_BLOCK : "VK_FORMAT_ASTC_4x4_SRGB_BLOCK", VK_FORMAT_ASTC_5x4_UNORM_BLOCK : "VK_FORMAT_ASTC_5x4_UNORM_BLOCK",
        VK_FORMAT_ASTC_5x4_SRGB_BLOCK : "VK_FORMAT_ASTC_5x4_SRGB_BLOCK", VK_FORMAT_ASTC_5x5_UNORM_BLOCK : "VK_FORMAT_ASTC_5x5_UNORM_BLOCK",
        VK_FORMAT_ASTC_5x5_SRGB_BLOCK : "VK_FORMAT_ASTC_5x5_SRGB_BLOCK", VK_FORMAT_ASTC_6x5_UNORM_BLOCK : "VK_FORMAT_ASTC_6x5_UNORM_BLOCK",
        VK_FORMAT_ASTC_6x5_SRGB_BLOCK : "VK_FORMAT_ASTC_6x5_SRGB_BLOCK", VK_FORMAT_ASTC_6x6_UNORM_BLOCK : "VK_FORMAT_ASTC_6x6_UNORM_BLOCK",
        VK_FORMAT_ASTC_6x6_SRGB_BLOCK : "VK_FORMAT_ASTC_6x6_SRGB_BLOCK", VK_FORMAT_ASTC_8x5_UNORM_BLOCK : "VK_FORMAT_ASTC_8x5_UNORM_BLOCK",
        VK_FORMAT_ASTC_8x5_SRGB_BLOCK : "VK_FORMAT_ASTC_8x5_SRGB_BLOCK", VK_FORMAT_ASTC_8x6_UNORM_BLOCK : "VK_FORMAT_ASTC_8x6_UNORM_BLOCK",
        VK_FORMAT_ASTC_8x6_SRGB_BLOCK : "VK_FORMAT_ASTC_8x6_SRGB_BLOCK", VK_FORMAT_ASTC_8x8_UNORM_BLOCK : "VK_FORMAT_ASTC_8x8_UNORM_BLOCK",
        VK_FORMAT_ASTC_8x8_SRGB_BLOCK : "VK_FORMAT_ASTC_8x8_SRGB_BLOCK", VK_FORMAT_ASTC_10x5_UNORM_BLOCK : "VK_FORMAT_ASTC_10x5_UNORM_BLOCK",
        VK_FORMAT_ASTC_10x5_SRGB_BLOCK : "VK_FORMAT_ASTC_10x5_SRGB_BLOCK", VK_FORMAT_ASTC_10x6_UNORM_BLOCK : "VK_FORMAT_ASTC_10x6_UNORM_BLOCK",
        VK_FORMAT_ASTC_10x6_SRGB_BLOCK : "VK_FORMAT_ASTC_10x6_SRGB_BLOCK", VK_FORMAT_ASTC_10x8_UNORM_BLOCK : "VK_FORMAT_ASTC_10x8_UNORM_BLOCK",
        VK_FORMAT_ASTC_10x8_SRGB_BLOCK : "VK_FORMAT_ASTC_10x8_SRGB_BLOCK", VK_FORMAT_ASTC_10x10_UNORM_BLOCK : "VK_FORMAT_ASTC_10x10_UNORM_BLOCK",
        VK_FORMAT_ASTC_10x10_SRGB_BLOCK : "VK_FORMAT_ASTC_10x10_SRGB_BLOCK", VK_FORMAT_ASTC_12x10_UNORM_BLOCK : "VK_FORMAT_ASTC_12x10_UNORM_BLOCK",
        VK_FORMAT_ASTC_12x10_SRGB_BLOCK : "VK_FORMAT_ASTC_12x10_SRGB_BLOCK", VK_FORMAT_ASTC_12x12_UNORM_BLOCK : "VK_FORMAT_ASTC_12x12_UNORM_BLOCK",
        VK_FORMAT_ASTC_12x12_SRGB_BLOCK : "VK_FORMAT_ASTC_12x12_SRGB_BLOCK"
    }

    return format_lookup[format]

def colorspace_to_string(colorspace):

    colorspace_lookup = {
        VK_COLOR_SPACE_SRGB_NONLINEAR_KHR : "VK_COLOR_SPACE_SRGB_NONLINEAR_KHR",
        VK_COLOR_SPACE_DISPLAY_P3_NONLINEAR_EXT : "VK_COLOR_SPACE_DISPLAY_P3_NONLINEAR_EXT",
        VK_COLOR_SPACE_EXTENDED_SRGB_LINEAR_EXT : "VK_COLOR_SPACE_EXTENDED_SRGB_LINEAR_EXT",
        VK_COLOR_SPACE_DCI_P3_NONLINEAR_EXT : "VK_COLOR_SPACE_DCI_P3_NONLINEAR_EXT",
        VK_COLOR_SPACE_BT709_LINEAR_EXT : "VK_COLOR_SPACE_BT709_LINEAR_EXT",
        VK_COLOR_SPACE_BT709_NONLINEAR_EXT : "VK_COLOR_SPACE_BT709_NONLINEAR_EXT",
        VK_COLOR_SPACE_BT2020_LINEAR_EXT : "VK_COLOR_SPACE_BT2020_LINEAR_EXT",
        VK_COLOR_SPACE_HDR10_ST2084_EXT : "VK_COLOR_SPACE_HDR10_ST2084_EXT",
        VK_COLOR_SPACE_DOLBYVISION_EXT : "VK_COLOR_SPACE_DOLBYVISION_EXT",
        VK_COLOR_SPACE_HDR10_HLG_EXT : "VK_COLOR_SPACE_HDR10_HLG_EXT",
        VK_COLOR_SPACE_ADOBERGB_LINEAR_EXT : "VK_COLOR_SPACE_ADOBERGB_LINEAR_EXT",
        VK_COLOR_SPACE_ADOBERGB_NONLINEAR_EXT : "VK_COLOR_SPACE_ADOBERGB_NONLINEAR_EXT",
        VK_COLOR_SPACE_PASS_THROUGH_EXT : "VK_COLOR_SPACE_PASS_THROUGH_EXT",
        VK_COLOR_SPACE_EXTENDED_SRGB_NONLINEAR_EXT : "VK_COLOR_SPACE_EXTENDED_SRGB_NONLINEAR_EXT"
    }

    return colorspace_lookup[colorspace]