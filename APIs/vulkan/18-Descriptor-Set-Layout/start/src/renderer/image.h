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

/**
* @brief Record an image layout transition onto a command buffer
* 
* @param commandBuffer to record to
* @param image the image whose layout to transition
* @param oldLayout the old layout
* @param newLayout the new layout
* @param srcAccessMask the operation after which to start transition
* @param dstAccessMask the operation which will wait on the transition
* @param srcStage the pipeline stage after which to start transition
* @param dstStage the pipeline stage which will wait on the transition
*/
void transition_image_layout(vk::CommandBuffer commandBuffer, vk::Image image,
    vk::ImageLayout oldLayout, vk::ImageLayout newLayout, 
    vk::AccessFlags srcAccessMask, vk::AccessFlags dstAccessMask,
    vk::PipelineStageFlags srcStage, vk::PipelineStageFlags dstStage);