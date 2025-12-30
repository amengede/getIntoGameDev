#include "sychronisation.h"
#include "../logging/logger.h"

vk::Semaphore make_semaphore(vk::Device& logicalDevice,
    std::deque<std::function<void(vk::Device)>>& deviceDeletionQueue) {

    Logger* logger = Logger::get_logger();

    /* Provided by VK_VERSION_1_0
    typedef struct VkSemaphoreCreateInfo {
        VkStructureType           sType;
        const void* pNext;
        VkSemaphoreCreateFlags    flags;
    } VkSemaphoreCreateInfo; */
    vk::SemaphoreCreateInfo semaphoreInfo;
    
    vk::Semaphore semaphore = logicalDevice.createSemaphore(semaphoreInfo).value;
    VkSemaphore handle = semaphore;

    deviceDeletionQueue.push_back([handle, logger](vk::Device device) {
        vkDestroySemaphore(device, handle, nullptr);
        logger->print("Destroyed semaphere");
    });

    return semaphore;
}

vk::Fence make_fence(vk::Device& logicalDevice,
    std::deque<std::function<void(vk::Device)>>& deviceDeletionQueue) {

    Logger* logger = Logger::get_logger();

    /* Provided by VK_VERSION_1_0
    typedef struct VkFenceCreateInfo {
        VkStructureType       sType;
        const void*           pNext;
        VkFenceCreateFlags    flags;
    } VkFenceCreateInfo; */
    vk::FenceCreateInfo fenceInfo;
    fenceInfo.setFlags(vk::FenceCreateFlagBits::eSignaled);

    vk::Fence fence = logicalDevice.createFence(fenceInfo).value;
    VkFence handle = fence;

    deviceDeletionQueue.push_back([handle, logger](vk::Device device) {
        vkDestroyFence(device, handle, nullptr);
        logger->print("Destroyed fence");
    });

    return fence;
}