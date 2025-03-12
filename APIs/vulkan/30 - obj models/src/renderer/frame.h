/*---------------------------------------------------------------------------*/
/*  Frame: Drawcall-Specific State
/*---------------------------------------------------------------------------*/
#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include "image.h"
#include "swapchain.h"
#include "../backend/memory.h"
#include <unordered_map>
#include "buffer.h"
#include "shader.h"
#include "descriptors.h"
#include "device.h"
#include "../math/math.h"

struct Bundle {
    mat4 proj;
    uint32_t triCount[4];
};

/**
 * @brief Holds all the state used in one
 *  rendering/presentation operation.
 */
class Frame {
public:

    /**
     * @brief Construct a new Frame object
     * 
     * @param swapchain swapchain to render to
     * @param logicalDevice vulkan device
     * @param shaders collection of compute shaders
     * @param dl Dynamic loader (for shader object functions)
     * @param commandBuffer command buffer
     * @param queue GPU Queue
     * @param descriptorSets Descriptor Sets for each binding scope
     * @param pipelineLayouts Layout of each pipeline
     * @param vertexBuffer Vertex Buffer
     * @param allocator Vulkan memory allocators
     * @param frameNumber the frame number (useful for debugging)
     */
    Frame(Swapchain& swapchain, Device& logicalDevice,
        std::unordered_map<PipelineType, vk::ShaderEXT>& shaders,
        vk::detail::DispatchLoaderDynamic& dl,
        vk::CommandBuffer commandBuffer,
        vk::Queue& queue,
        std::unordered_map<DescriptorScope, vk::DescriptorSet>& descriptorSets,
        std::unordered_map<PipelineType, vk::PipelineLayout>& pipelineLayouts,
        Buffer* vertexBuffer,
        std::unordered_map<AllocatorScope, mem::Allocator>& allocators,
        int frameNumber);

    /**
    * @brief Record the command buffer
    *
    * @param imageIndex Image Index to draw to
    */
    void record_command_buffer(uint32_t imageIndex);

    /**
    * @brief free any resources owned by the frame
    */
    void free_resources(AllocatorScope scope);

    /**
    * @brief Rebuild the frame.
    * 
    * @param vertexBuffer Vertex Buffer to render.
    */
    void rebuild(Buffer* vertexBuffer);

    /**
    * @brief build frame resources
    */
    void build(Buffer* vertexBuffer);

    /**
    * @brief signalled upon successful image aquisition from swapchain
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
    * @brief for recording drawing commands
    */
    vk::CommandBuffer commandBuffer;

    Buffer* vertexBuffer;

private:

    /**
    * @brief clear the screen
    */
    void clear_screen();

    /**
    * @brief draw a big triangles
    */
    void draw_big_triangle();

    /**
    * @brief draw small triangles
    */
    void draw_small_triangles();

    /**
    * @brief extract color from depth/color buffer
    */
    void resolve_to_color_buffer();

    /**
    * @brief Vulkan logical device
    */
    Device logicalDevice;

    /**
    * @brief swapchain swapchain to render to
    */
    Swapchain& swapchain;

    /**
    * @brief collection of compute shaders
    */
    std::unordered_map<PipelineType, vk::ShaderEXT>& shaders;

    /**
    * @brief Dynamic loader (for shader object functions)
    */
    vk::detail::DispatchLoaderDynamic& dl;

    /**
    * @brief Descriptor Sets for each binding scope
    */
    std::unordered_map<DescriptorScope, vk::DescriptorSet>& descriptorSets;

    /**
    * @brief Layout of each pipeline
    */
    std::unordered_map<PipelineType, vk::PipelineLayout>& pipelineLayouts;

    /**
    * @brief Allocator
    */
    std::unordered_map<AllocatorScope, mem::Allocator>& allocators;

    /**
    * @brief Depth & Color Buffer
    */
    StorageImage* depthColorBuffer;

    /**
    * @brief Color Buffer
    */
    StorageImage* colorBuffer;

    /**
    * @brief GPU queue for work submission
    */
    vk::Queue& queue;

    /**
    * @brief index of this frame, used for debugging
    */
    int frameNumber;

    /**
    * @brief Uniform Buffer object (projection matrix)
    */
    Buffer UBO;
};
/*---------------------------------------------------------------------------*/