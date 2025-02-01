from config import *
import logging
import queue_families

"""
    Vulkan separates the concept of physical and logical devices. 

    A physical device usually represents a single complete implementation of Vulkan 
    (excluding instance-level functionality) available to the host, 
    of which there are a finite number. 
  
    A logical device represents an instance of that implementation 
    with its own state and resources independent of other logical devices.
"""

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

def create_logical_device(physicalDevice, instance, surface, debug):

    """
        Create an abstraction around the GPU
    """

    """
        At time of creation, any required queues will also be created,
        so queue create info must be passed in
    """
    indices = queue_families.find_queue_families(physicalDevice, instance, surface, debug)
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

    indices = queue_families.find_queue_families(physicalDevice, instance, surface, debug)
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
