#include "frame.h"

Frame::Frame(vk::Image image, vk::Device logicalDevice,
    vk::Format swapchainFormat,
    std::deque<std::function<void(vk::Device)>>& deletionQueue): image(image) {
    
    imageView = create_image_view(
        logicalDevice, image, swapchainFormat);
    VkImageView imageViewHandle = imageView;
    deletionQueue.push_back([imageViewHandle](vk::Device device) {
        vkDestroyImageView(device, imageViewHandle, nullptr);
    });
}