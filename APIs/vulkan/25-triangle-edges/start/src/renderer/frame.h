#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include "image.h"
#include <deque>
#include <functional>
#include "swapchain.h"
#include "vma/vk_mem_alloc.h"
#include "../factories/mesh_factory.h"

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
     * @param shader compute shader
     * @param dl Dynamic loader (for shader object functions)
     * @param commandBuffer command buffer
     * @param queue GPU Queue
     * @param deletionQueue deletion queue
     * @param descriptorSet Descriptor Set for compute shader
     * @param pipelineLayout Pipeline Layout
     * @param allocator Vulkan memory allocator
     */
    Frame(Swapchain& swapchain, vk::Device& logicalDevice, 
        vk::ShaderEXT* shaders,
        vk::DispatchLoaderDynamic& dl,
        vk::CommandBuffer commandBuffer,
        vk::Queue& queue,
        std::deque<std::function<void(vk::Device)>>& deletionQueue,
        vk::DescriptorSet& clearDescriptorSet,
        vk::PipelineLayout& clearPipelineLayout,
        vk::DescriptorSet& rasterizeDescriptorSet,
        vk::PipelineLayout& rasterizePipelineLayout,
        VmaAllocator& allocator, Mesh* vertexBuffer);

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
    * @brief free any resources owned by the frame
    */
    void free_resources();

    vk::Device& logicalDevice;

    /**
    * @brief for recording drawing commands
    * 
    */
    vk::CommandBuffer commandBuffer;

    Swapchain& swapchain;
    vk::ShaderEXT* shaders;
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

    vk::PipelineLayout& clearPipelineLayout;
    vk::DescriptorSet& clearDescriptorSet;

    vk::PipelineLayout& rasterizePipelineLayout;
    vk::DescriptorSet& rasterizeDescriptorSet;

    VmaAllocator& allocator;
    StorageImage* colorBuffer;

    std::deque<std::function<void(VmaAllocator)>> vmaDeletionQueue;
    std::deque<std::function<void(vk::Device)>> deviceDeletionQueue;

    vk::Queue queue;

    Mesh* vertexBuffer;

};