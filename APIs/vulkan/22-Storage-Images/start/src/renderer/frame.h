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
    Frame(Swapchain& swapchain, vk::Device& logicalDevice, 
        vk::ShaderEXT& shader,
        vk::DispatchLoaderDynamic& dl,
        vk::CommandBuffer commandBuffer,
        std::deque<std::function<void(vk::Device)>>& deletionQueue,
        vk::DescriptorSet& descriptorSet,
        vk::PipelineLayout& pipelineLayout);

    /**
    * @brief Set (and record) the command buffer
    *
    * @param newCommandBuffer the command buffer to record to
    * @param shaders shader objects to use
    * @param framesize size of the screen
    * @param dl dynamic loader
    */
    void record_command_buffer(uint32_t imageIndex);

    /**
    * @brief for recording drawing commands
    * 
    */
    vk::CommandBuffer commandBuffer;

    Swapchain& swapchain;
    vk::ShaderEXT& shader;
    vk::DispatchLoaderDynamic& dl;

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

    vk::PipelineLayout& pipelineLayout;
    vk::DescriptorSet& descriptorSet;

};