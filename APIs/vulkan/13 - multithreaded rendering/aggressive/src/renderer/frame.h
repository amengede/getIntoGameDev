#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include "image.h"
#include <deque>
#include <functional>
#include "swapchain.h"

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
    Frame(vk::DispatchLoaderDynamic& dl,
        vk::Device& logicalDevice,
        std::deque<std::function<void(vk::Device)>>& deviceDeletionQueue,
        vk::CommandBuffer commandBuffer,
        Swapchain& swapchain,
        std::vector<vk::ShaderEXT>& shaders,
        vk::Queue& queue);

    /**
    * @brief Record the command buffer
    */
    void record_draw_commands();

    /**
    * @brief for recording drawing commands
    * 
    */
    vk::CommandBuffer commandBuffer;

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

    /**
    * @brief the image index in the swapchain to ultimately present to
    */
    uint32_t imageIndex;

    void acquire_image();

    void render();

    void present();

private:

    /**
    * @brief title says it all
    *
    */
    void annoying_boilerplate_that_dynamic_rendering_was_meant_to_spare_us();

    vk::RenderingInfoKHR renderingInfo = {};

    vk::RenderingAttachmentInfoKHR colorAttachment = {};

    vk::Device& logicalDevice;

    Swapchain& swapchain;

    std::vector<vk::ShaderEXT>& shaders;

    vk::DispatchLoaderDynamic& dl;

    vk::Queue& queue;

};