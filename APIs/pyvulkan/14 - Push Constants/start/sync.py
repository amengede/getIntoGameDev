from config import *

def make_semaphore(device, debug):

    semaphoreInfo = VkSemaphoreCreateInfo()

    try:

        return vkCreateSemaphore(device, semaphoreInfo, None)
    
    except:

        if debug:
            print("Failed to create semaphore")
        
        return None

def make_fence(device, debug):

    fenceInfo = VkFenceCreateInfo(
        flags = VK_FENCE_CREATE_SIGNALED_BIT
    )

    try:

        return vkCreateFence(device, fenceInfo, None)
    
    except:

        if debug:
            print("Failed to create fence")
        
        return None