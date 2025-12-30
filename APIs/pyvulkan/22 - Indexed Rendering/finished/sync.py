from config import *
import vklogging

def make_semaphore(device):

    semaphoreInfo = VkSemaphoreCreateInfo()

    try:

        return vkCreateSemaphore(device, semaphoreInfo, None)
    
    except:

        vklogging.logger.print("Failed to create semaphore")
        
        return None

def make_fence(device):

    fenceInfo = VkFenceCreateInfo(
        flags = VK_FENCE_CREATE_SIGNALED_BIT
    )

    try:

        return vkCreateFence(device, fenceInfo, None)
    
    except:

        vklogging.logger.print("Failed to create fence")
        
        return None