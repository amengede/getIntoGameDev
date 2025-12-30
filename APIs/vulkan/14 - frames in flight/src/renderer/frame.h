#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include "image.h"
#include "swapchain.h"
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
     * @param swapchain swapchain to render to
     * @param commandBuffer for recording drawing commands and resource transitions
     * @param shaders the shader objects to use in rendering
     * @param dl dynamic loader for all those weird modern features we're using
     */
    Frame(vk::Device& logicalDevice,
        Swapchain& swapchain,
        vk::CommandBuffer commandBuffer,
        std::vector<vk::ShaderEXT>& shaders,
        vk::DispatchLoaderDynamic& dl,
        std::deque<std::function<void(vk::Device)>>& deviceDeletionQueue);

    /**
     * @brief swapchain to render to
     */
    Swapchain& swapchain;

    /**
    * @brief for recording drawing commands and resource transitions
    *
    */
    vk::CommandBuffer commandBuffer;

    /**
     * @brief shaders the shader objects to use in rendering
     */
    std::vector<vk::ShaderEXT>& shaders;

    /**
     * @brief dl dynamic loader for all those weird modern features we're using
     */
    vk::DispatchLoaderDynamic& dl;

    /**
    * @brief Record the command buffer so that it will render to the given
    * image index.
    *
    * @param imageIndex image index within the swapchain to render to
    */
    void record_command_buffer(uint32_t imageIndex);

    /**
    * @brief signalled upon successful image aquisition from swapchain
    *
    */
    vk::Semaphore imageAquiredSemaphore;

    /**
    * @brief signalled upon successful render of an image
    */
    vk::Semaphore renderFinishedSemaphore;

    /**
    * @brief signalled upon successful render of an image
    */
    vk::Fence renderFinishedFence;

private:

    /**
    * @brief Build a description of the rendering info
    */
    void build_rendering_info();

    /**
    * @brief build a description of the color attachment
    *
    */
    void build_color_attachment(uint32_t imageIndex);

    /**
    * @brief title says it all
    *
    */
    void annoying_boilerplate_that_dynamic_rendering_was_meant_to_spare_us();

    vk::RenderingInfoKHR renderingInfo = {};

    vk::RenderingAttachmentInfoKHR colorAttachment = {};

};