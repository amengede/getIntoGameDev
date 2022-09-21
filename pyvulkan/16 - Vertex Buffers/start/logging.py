from config import *
import os

def debugCallback(*args):
    """
        Callback function for validation layers/debugging.
    """

    
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

    print(f"Validation Layer: {args[5]} {args[6]}")
    return 0

def make_debug_messenger(instance):
    """
        Make a debug report callback for validation layers to call

        Parameters:
            instance (VkInstance): The vulkan instance whose validation layers
            will use the callback function.
    """

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

class Logger:
    """
        Static class for debug logging (printing custom info to the console).
    """

    def __init__(self):
        """
            Create the logger.
        """

        self.debug_mode = False

        self.physical_device_types = {
            VK_PHYSICAL_DEVICE_TYPE_CPU: "CPU",
            VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU: "Discrete GPU",
            VK_PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU: "Integrated GPU",
            VK_PHYSICAL_DEVICE_TYPE_VIRTUAL_GPU: "Virtual GPU",
            VK_PHYSICAL_DEVICE_TYPE_OTHER: "Other"
        }

        self.colorspace_lookup = {
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

        self.format_lookup = {
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

        self.present_mode_lookup = {
            VK_PRESENT_MODE_IMMEDIATE_KHR: """immediate: the presentation engine does not wait for a vertical blanking period 
    to update the current image, meaning this mode may result in visible tearing. No internal 
    queuing of presentation requests is needed, as the requests are applied immediately.""",
            VK_PRESENT_MODE_MAILBOX_KHR: """mailbox: the presentation engine waits for the next vertical blanking period 
    to update the current image. Tearing cannot be observed. An internal single-entry queue is 
    used to hold pending presentation requests. If the queue is full when a new presentation 
    request is received, the new request replaces the existing entry, and any images associated 
    with the prior entry become available for re-use by the application. One request is removed 
    from the queue and processed during each vertical blanking period in which the queue is non-empty.""",
            VK_PRESENT_MODE_FIFO_KHR: """fifo: the presentation engine waits for the next vertical blanking 
    period to update the current image. Tearing cannot be observed. An internal queue is used to 
    hold pending presentation requests. New requests are appended to the end of the queue, and one 
    request is removed from the beginning of the queue and processed during each vertical blanking 
    period in which the queue is non-empty. This is the only value of presentMode that is required 
    to be supported.""",
            VK_PRESENT_MODE_FIFO_RELAXED_KHR: """relaxed fifo: the presentation engine generally waits for the next vertical 
    blanking period to update the current image. If a vertical blanking period has already passed 
    since the last update of the current image then the presentation engine does not wait for 
    another vertical blanking period for the update, meaning this mode may result in visible tearing 
    in this case. This mode is useful for reducing visual stutter with an application that will 
    mostly present a new image before the next vertical blanking period, but may occasionally be 
    late, and present a new image just after the next vertical blanking period. An internal queue 
    is used to hold pending presentation requests. New requests are appended to the end of the queue, 
    and one request is removed from the beginning of the queue and processed during or after each 
    vertical blanking period in which the queue is non-empty.""",
            VK_PRESENT_MODE_SHARED_DEMAND_REFRESH_KHR: """shared demand refresh: the presentation engine and application have 
    concurrent access to a single image, which is referred to as a shared presentable image. 
    The presentation engine is only required to update the current image after a new presentation 
    request is received. Therefore the application must make a presentation request whenever an 
    update is required. However, the presentation engine may update the current image at any point, 
    meaning this mode may result in visible tearing.""",
            VK_PRESENT_MODE_SHARED_CONTINUOUS_REFRESH_KHR: """shared continuous refresh: the presentation engine and application have 
    concurrent access to a single image, which is referred to as a shared presentable image. The 
    presentation engine periodically updates the current image on its regular refresh cycle. The 
    application is only required to make one initial presentation request, after which the 
    presentation engine must update the current image without any need for further presentation 
    requests. The application can indicate the image contents have been updated by making a 
    presentation request, but this does not guarantee the timing of when it will be updated. 
    This mode may result in visible tearing if rendering to the image is not timed correctly."""
        }
    
    def set_debug_mode(self, debug_mode: bool) -> None:
        """
            Set the logger's debug mode

            Parameters:
                debug_mode (bool): The new debug mode to use
        """

        self.debug_mode = debug_mode

    def _extract_version_number(self, version: int) -> tuple[int, int, int, int]:
        """
            Extract the variant, major, minor and patch versions from a version number

            Parameters:
                version (int): The version number, packed into a 32 bit integer
            
            Returns:
                tuple[int, int, int, int]: Variant, Major, Minor and Patch version numbers
        """

        return (
            version >> 29, 
            VK_VERSION_MAJOR(version),
            VK_VERSION_MINOR(version),
            VK_VERSION_PATCH(version)
        )
    
    def _extract_driver_version_nvidia(self, version: int) -> str:
        """
            Extract the graphics driver number,
            according to nvidia's conventions

            Parameters:
                version (int): The version number, packed into a 32 bit integer
            
            Returns:
                str: The Nvidia driver number
        """

        return f"{(version >> 22) & 0x3ff}.{(version >> 14) & 0x0ff}.{(version >> 6) & 0x0ff}.{version & 0x003f}"

    def _extract_driver_version_intel(self, version: int) -> str:
        """
            Extract the graphics driver number,
            according to intel's conventions under windows

            Parameters:
                version (int): The version number, packed into a 32 bit integer
            
            Returns:
                str: The Intel driver number
        """

        return f"{version >> 14}.{version & 0x3fff}"
    
    def _extract_driver_version_standard(self, version: int) -> str:
        """
            Extract the graphics driver number,
            where no vendor convention is available.

            Parameters:
                version (int): The version number, packed into a 32 bit integer
            
            Returns:
                str: The Intel driver number
        """

        return f"{version >> 22}.{(version >> 12) & 0x3ff}.{version & 0xfff}"
    
    def _log_physical_device_limits(self, limits) -> None:
        """
            Log various device limits.

            Parameters:
                limits (VkPhysicalDeviceLimits): the device limits struct
        """

        """
            typedef struct VkPhysicalDeviceLimits {
        uint32_t              maxImageDimension1D;
        uint32_t              maxImageDimension2D;
        uint32_t              maxImageDimension3D;
        uint32_t              maxImageDimensionCube;
        uint32_t              maxImageArrayLayers;
        uint32_t              maxTexelBufferElements;
        uint32_t              maxUniformBufferRange;
        uint32_t              maxStorageBufferRange;
        uint32_t              maxPushConstantsSize;
        uint32_t              maxMemoryAllocationCount;
        uint32_t              maxSamplerAllocationCount;
        VkDeviceSize          bufferImageGranularity;
        VkDeviceSize          sparseAddressSpaceSize;
        uint32_t              maxBoundDescriptorSets;
        uint32_t              maxPerStageDescriptorSamplers;
        uint32_t              maxPerStageDescriptorUniformBuffers;
        uint32_t              maxPerStageDescriptorStorageBuffers;
        uint32_t              maxPerStageDescriptorSampledImages;
        uint32_t              maxPerStageDescriptorStorageImages;
        uint32_t              maxPerStageDescriptorInputAttachments;
        uint32_t              maxPerStageResources;
        uint32_t              maxDescriptorSetSamplers;
        uint32_t              maxDescriptorSetUniformBuffers;
        uint32_t              maxDescriptorSetUniformBuffersDynamic;
        uint32_t              maxDescriptorSetStorageBuffers;
        uint32_t              maxDescriptorSetStorageBuffersDynamic;
        uint32_t              maxDescriptorSetSampledImages;
        uint32_t              maxDescriptorSetStorageImages;
        uint32_t              maxDescriptorSetInputAttachments;
        uint32_t              maxVertexInputAttributes;
        uint32_t              maxVertexInputBindings;
        uint32_t              maxVertexInputAttributeOffset;
        uint32_t              maxVertexInputBindingStride;
        uint32_t              maxVertexOutputComponents;
        uint32_t              maxTessellationGenerationLevel;
        uint32_t              maxTessellationPatchSize;
        uint32_t              maxTessellationControlPerVertexInputComponents;
        uint32_t              maxTessellationControlPerVertexOutputComponents;
        uint32_t              maxTessellationControlPerPatchOutputComponents;
        uint32_t              maxTessellationControlTotalOutputComponents;
        uint32_t              maxTessellationEvaluationInputComponents;
        uint32_t              maxTessellationEvaluationOutputComponents;
        uint32_t              maxGeometryShaderInvocations;
        uint32_t              maxGeometryInputComponents;
        uint32_t              maxGeometryOutputComponents;
        uint32_t              maxGeometryOutputVertices;
        uint32_t              maxGeometryTotalOutputComponents;
        uint32_t              maxFragmentInputComponents;
        uint32_t              maxFragmentOutputAttachments;
        uint32_t              maxFragmentDualSrcAttachments;
        uint32_t              maxFragmentCombinedOutputResources;
        uint32_t              maxComputeSharedMemorySize;
        uint32_t              maxComputeWorkGroupCount[3];
        uint32_t              maxComputeWorkGroupInvocations;
        uint32_t              maxComputeWorkGroupSize[3];
        uint32_t              subPixelPrecisionBits;
        uint32_t              subTexelPrecisionBits;
        uint32_t              mipmapPrecisionBits;
        uint32_t              maxDrawIndexedIndexValue;
        uint32_t              maxDrawIndirectCount;
        float                 maxSamplerLodBias;
        float                 maxSamplerAnisotropy;
        uint32_t              maxViewports;
        uint32_t              maxViewportDimensions[2];
        float                 viewportBoundsRange[2];
        uint32_t              viewportSubPixelBits;
        size_t                minMemoryMapAlignment;
        VkDeviceSize          minTexelBufferOffsetAlignment;
        VkDeviceSize          minUniformBufferOffsetAlignment;
        VkDeviceSize          minStorageBufferOffsetAlignment;
        int32_t               minTexelOffset;
        uint32_t              maxTexelOffset;
        int32_t               minTexelGatherOffset;
        uint32_t              maxTexelGatherOffset;
        float                 minInterpolationOffset;
        float                 maxInterpolationOffset;
        uint32_t              subPixelInterpolationOffsetBits;
        uint32_t              maxFramebufferWidth;
        uint32_t              maxFramebufferHeight;
        uint32_t              maxFramebufferLayers;
        VkSampleCountFlags    framebufferColorSampleCounts;
        VkSampleCountFlags    framebufferDepthSampleCounts;
        VkSampleCountFlags    framebufferStencilSampleCounts;
        VkSampleCountFlags    framebufferNoAttachmentsSampleCounts;
        uint32_t              maxColorAttachments;
        VkSampleCountFlags    sampledImageColorSampleCounts;
        VkSampleCountFlags    sampledImageIntegerSampleCounts;
        VkSampleCountFlags    sampledImageDepthSampleCounts;
        VkSampleCountFlags    sampledImageStencilSampleCounts;
        VkSampleCountFlags    storageImageSampleCounts;
        uint32_t              maxSampleMaskWords;
        VkBool32              timestampComputeAndGraphics;
        float                 timestampPeriod;
        uint32_t              maxClipDistances;
        uint32_t              maxCullDistances;
        uint32_t              maxCombinedClipAndCullDistances;
        uint32_t              discreteQueuePriorities;
        float                 pointSizeRange[2];
        float                 lineWidthRange[2];
        float                 pointSizeGranularity;
        float                 lineWidthGranularity;
        VkBool32              strictLines;
        VkBool32              standardSampleLocations;
        VkDeviceSize          optimalBufferCopyOffsetAlignment;
        VkDeviceSize          optimalBufferCopyRowPitchAlignment;
        VkDeviceSize          nonCoherentAtomSize;
    } VkPhysicalDeviceLimits;
        """
        print("Physical Device Limits:")
        print(f"\tMaximum 1D Image Size: {limits.maxImageDimension1D}")
        print(f"\tMaximum 2D Image Size: {limits.maxImageDimension2D}")
        print(f"\tMaximum 3D Image Size: {limits.maxImageDimension3D}")
        print(f"\tMaximum 2D Cube Image Size: {limits.maxImageDimensionCube}")
        print(f"\tMaximum Image Array Layers: {limits.maxImageArrayLayers}")
        print(f"\tMaximum Descriptor Sets per stage: {limits.maxBoundDescriptorSets}")
        print(f"\tMaximum Sampler Descriptors per stage: {limits.maxPerStageDescriptorSamplers}")

    def log_device_properties(self, device) -> None:
        """
            Print out the properties of a physical device to the console.

            Parameters:

                device (VkPhysicalDevice): the physical device to query and log
        """

        if not self.debug_mode:
            return
        
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

        variant, major, minor, patch = self._extract_version_number(properties.apiVersion)
        print(f"Device API version: Variant: {variant}, Major: {major}, Minor: {minor}, Patch: {patch}")

        # driverVersion: convention as to how driver numbers are packed is vendor-specific
        if (properties.vendorID == 4318):
            print("----Nvidia Card Detected----")
            driver_version = self._extract_driver_version_nvidia(properties.driverVersion)
        elif (os.name == "nt" and properties.vendorID == 0x8086):
            print("----Intel Windows Detected----")
            driver_version = self._extract_driver_version_intel(properties.driverVersion)
        else:
            print("----Fallback to standard Vulkan Versioning----")
            driver_version = self._extract_driver_version_standard(properties.driverVersion)
        print(f"Device driver version: {driver_version}")

        if properties.deviceType in self.physical_device_types:
            print("Device type: ",end="")
            print(self.physical_device_types[properties.deviceType])
        
        print(f"Device name: {properties.deviceName}")

        print("Pipline cache Universally Unique ID: ", end="")
        for byte in properties.pipelineCacheUUID:
            print(byte, end=" ")
        print()

        self._log_physical_device_limits(properties.limits)

    def _log_transform_bits(self, bits: int) -> list[str]:
        """
            Fetch the Transform types from a given flag.

            Parameters:
                bits (int): The integer representing a set of transforms.
            
            Returns:
                list[str]: The transforms contained in the integer flag.
        """

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

    def _log_alpha_composite_bits(self, bits: int) -> list[str]:
        """
            Extract the various composite alpha modes from the provided bitmask

            Parameters:
                bits (int): The provided bitmask, stores a bunch of composite alpha modes
            
            Returns:
                list[str]: Describes the composite alpha modes in the bitmask
        """
        
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

    def _log_image_usage_bits(self, bits: int) -> list[str]:
        """
            Extract the various image usage modes from the provided bitmask

            Parameters:
                bits (int): The provided bitmask, stores a bunch of image usage modes
            
            Returns:
                list[str]: Describes the image usage modes in the bitmask
        """

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

    def print(self, message: str) -> None:
        """
            Simple function for printing simple things.
        """

        if not self.debug_mode:
            return

        print(message)
    
    def log_list(self, items: list[str]) -> None:
        """
            Print out a general list of items
        """

        if not self.debug_mode:
            return

        for item in items:
            print(f"\t\"{item}\"")
    
    def log_surface_capabilities(self, support) -> None:
        """
            Logs the capabilities of a Vulkan Surface.

            Prarameters:
                support (VkSurfaceCapabilitiesKHR): describes swapchain support
        """

        if not self.debug_mode:
            return


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
        stringList = self._log_transform_bits(support.capabilities.supportedTransforms)
        for line in stringList:
            print(f"\t\t{line}")

        print("\tcurrent transform:")
        stringList = self._log_transform_bits(support.capabilities.currentTransform)
        for line in stringList:
            print(f"\t\t{line}")

        print("\tsupported alpha operations:")
        stringList = self._log_alpha_composite_bits(support.capabilities.supportedCompositeAlpha)
        for line in stringList:
            print(f"\t\t{line}")

        print("\tsupported image usage:")
        stringList = self._log_image_usage_bits(support.capabilities.supportedUsageFlags)
        for line in stringList:
            print(f"\t\t{line}")
    
    def log_surface_format(self, surface_format) -> None:
        """
            Print out the format and color space of the given format.

            Parameters:
                surface_format (VkSurfaceFormatKHR): The given format
        """

        if not self.debug_mode:
            return
        
        """
            * typedef struct VkSurfaceFormatKHR {
                VkFormat           format;
                VkColorSpaceKHR    colorSpace;
            } VkSurfaceFormatKHR;
        """

        print(f"supported pixel format: {self.format_lookup[surface_format.format]}")
        print(f"supported color space: {self.colorspace_lookup[surface_format.colorSpace]}")

    
logger = Logger()