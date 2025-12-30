#include "frame.h"

Frame::Frame(vk::Image image, vk::Device logicalDevice,
    vk::Format swapchainFormat,
    std::deque<std::function<void(vk::Device)>>& deletionQueue): image(image) {
}