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
    * @brief Set (and record) the command buffer
    *
    * @param newCommandBuffer the command buffer to record to
    * @param shaders shader objects to use
    * @param framesize size of the screen
    * @param dl dynamic loader
    */
    void set_command_buffer(vk::CommandBuffer newCommandBuffer,
        std::vector<vk::ShaderEXT>& shaders, vk::Extent2D frameSize,
        vk::detail::DispatchLoaderDynamic& dl);

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

    /**
    * @brief for recording drawing commands
    * 
    */
    vk::CommandBuffer commandBuffer;

private:

    /**
    * @brief Build a description of the rendering info
    *
    * @param framesize size of the screen
    */
    void build_rendering_info(vk::Extent2D frameSize);

    /**
    * @brief build a description of the color attachment
    *
    */
    void build_color_attachment();

    /**
    * @brief title says it all
    *
    */
    void annoying_boilerplate_that_dynamic_rendering_was_meant_to_spare_us(
        vk::Extent2D frameSize, vk::detail::DispatchLoaderDynamic& dl);

    vk::RenderingInfoKHR renderingInfo = {};

    vk::RenderingAttachmentInfoKHR colorAttachment = {};

};