#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>

/**
 * @brief Create a image view object
 * 
 * @param logicalDevice the vulkan device
 * @param image image to view
 * @param format image format
 * @return vk::ImageView the created image view
 */
vk::ImageView create_image_view(vk::Device logicalDevice, 
    vk::Image image, vk::Format format);