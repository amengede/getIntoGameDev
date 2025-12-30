#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include "image.h"
#include <deque>
#include <functional>

/**
 * @brief Holds all the state used in one
 *  rendering/presentation operation.
 * 
 */
class Frame {
public:

    /**
     * @brief Construct a new Frame object
     * 
     * @param image swapchain image to render to
     * @param logicalDevice vulkan device
     * @param deletionQueue deletionQueue
     * @param swapchainFormat swapchain image format
     */
    Frame(vk::Image image, vk::Device logicalDevice, 
        vk::Format swapchainFormat,
        std::deque<std::function<void(vk::Device)>>& deletionQueue);

    /**
     * @brief swapchain image to render to
     * 
     */
    vk::Image image;

    /**
     * @brief view of the swapchain image
     * 
     */
    vk::ImageView imageView;
};