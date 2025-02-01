from config import *

def start_job(commandBuffer):

    vkResetCommandBuffer(
        commandBuffer = commandBuffer,
        flags = 0
    )

    beginInfo = VkCommandBufferBeginInfo(
        flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT
    )
    vkBeginCommandBuffer(
        commandBuffer = commandBuffer, pBeginInfo = beginInfo
    )

def end_job(commandBuffer, queue):

    vkEndCommandBuffer(commandBuffer = commandBuffer)

    submitInfo = VkSubmitInfo(
        commandBufferCount = 1, pCommandBuffers = [commandBuffer,]
    )
    vkQueueSubmit(
        queue = queue, submitCount = 1, pSubmits = [submitInfo,],
        fence = None
    )

    vkQueueWaitIdle(queue = queue)