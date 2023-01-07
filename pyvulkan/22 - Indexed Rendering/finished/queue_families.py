from config import *
import vklogging

class QueueFamilyIndices:


    def __init__(self):

        self.graphicsFamily = None
        self.presentFamily = None
    
    def is_complete(self):

        return not(self.graphicsFamily is None or self.presentFamily is None)
    
def find_queue_families(device, instance, surface):
        
    indices = QueueFamilyIndices()

    surfaceSupport = vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceSurfaceSupportKHR")

    queueFamilies = vkGetPhysicalDeviceQueueFamilyProperties(device)

    vklogging.logger.print(
        f"There are {len(queueFamilies)} queue families available on the system."
    )

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
            vklogging.logger.print(f"Queue Family {i} is suitable for graphics")
        
        if surfaceSupport(device, i, surface):
            indices.presentFamily = i
            vklogging.logger.print(f"Queue Family {i} is suitable for presenting")

        if indices.is_complete():
            break

    return indices