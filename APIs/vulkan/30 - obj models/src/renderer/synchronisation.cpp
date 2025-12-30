#include "synchronisation.h"
#include "../logging/logger.h"

vk::Semaphore make_semaphore(Device& logicalDevice) {

    Logger* logger = Logger::get_logger();

    /* Provided by VK_VERSION_1_0
    typedef struct VkSemaphoreCreateInfo {
        VkStructureType           sType;
        const void* pNext;
        VkSemaphoreCreateFlags    flags;
    } VkSemaphoreCreateInfo; */
    vk::SemaphoreCreateInfo semaphoreInfo;
    
    vk::Semaphore semaphore = logicalDevice.device.createSemaphore(semaphoreInfo).value;
    VkSemaphore handle = semaphore;

    logicalDevice.deletionQueue.push_back([handle, logger](vk::Device device) {
        vkDestroySemaphore(device, handle, nullptr);
        logger->print("Destroyed semaphere");
    });

    return semaphore;
}

vk::Fence make_fence(Device& logicalDevice) {

    Logger* logger = Logger::get_logger();

    /* Provided by VK_VERSION_1_0
    typedef struct VkFenceCreateInfo {
        VkStructureType       sType;
        const void*           pNext;
        VkFenceCreateFlags    flags;
    } VkFenceCreateInfo; */
    vk::FenceCreateInfo fenceInfo;
    fenceInfo.setFlags(vk::FenceCreateFlagBits::eSignaled);

    vk::Fence fence = logicalDevice.device.createFence(fenceInfo).value;
    VkFence handle = fence;

    logicalDevice.deletionQueue.push_back([handle, logger](vk::Device device) {
        vkDestroyFence(device, handle, nullptr);
        logger->print("Destroyed fence");
    });

    return fence;
}