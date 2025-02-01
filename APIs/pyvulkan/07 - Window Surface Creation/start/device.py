import queue
from config import *

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
            log_device_properties(device)
        if is_suitable(device, debug):
            return device

    return None

def find_queue_families(device, debug):
        
    indices = QueueFamilyIndices()

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
            indices.presentFamily = i

            if debug:
                print(f"Queue Family {i} is suitable for graphics and presenting")

            if indices.is_complete():
                break

    return indices

def create_logical_device(physicalDevice, debug):

    """
        Create an abstraction around the GPU
    """

    """
        At time of creation, any required queues will also be created,
        so queue create info must be passed in
    """
    indices = find_queue_families(physicalDevice, debug)
    queueCreateInfo = VkDeviceQueueCreateInfo(
        queueFamilyIndex = indices.graphicsFamily,
        queueCount = 1,
        pQueuePriorities = [1.0,]
    )

    """
        Device features must be requested before the device is abstracted,
        therefore we only pay for what we use
    """
    deviceFeatures = VkPhysicalDeviceFeatures()

    enabledLayers = []
    if debug:
        enabledLayers.append("VK_LAYER_KHRONOS_validation")

    createInfo = VkDeviceCreateInfo(
        queueCreateInfoCount = 1,
        pQueueCreateInfos = [queueCreateInfo,],
        enabledExtensionCount = 0,
        pEnabledFeatures = [deviceFeatures,],
        enabledLayerCount = len(enabledLayers),
        ppEnabledLayerNames = enabledLayers
    )

    return vkCreateDevice(
        physicalDevice = physicalDevice, pCreateInfo = [createInfo,], pAllocator = None
    )

def get_queue(physicalDevice, logicalDevice, debug):

    indices = find_queue_families(physicalDevice, debug)
    return vkGetDeviceQueue(
        device = logicalDevice,
        queueFamilyIndex = indices.graphicsFamily,
        queueIndex = 0
    )