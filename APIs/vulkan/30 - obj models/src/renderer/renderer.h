/*---------------------------------------------------------------------------*/
/*  Renderer
/*---------------------------------------------------------------------------*/
#pragma once
#undef VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include <GLFW/glfw3.h>
#include <deque>
#include <functional>
#include "frame.h"
#include "swapchain.h"
#include "../backend/memory.h"
#include <unordered_map>
#include "../backend/dynamic_array.h"
#include <vector>
#include "device.h"

/**
 * @brief Vroom vroom.
 */
class Engine {

public:

    /**
     * @brief Construct a new Engine object
     *
     * @param window main window to render to
     */
    Engine(GLFWwindow* window);

    /**
     * @brief Destroy the Engine object
     */
    ~Engine();

    /**
    * @brief draw something!
    */
    void draw();

private:

    /**
    * @brief Make instance
    */
    void make_instance_stuff();

    /**
    * @brief Make physical and logical device
    */
    void make_device_stuff();

    /**
    * @brief Make VMA
    */
    void make_allocators();

    /**
    * @brief make swapchain
    */
    void build_swapchain();

    /**
    * @brief Make descriptor set layouts
    */
    void make_descriptor_set_layouts();

    void make_pipeline_layouts();

    void make_shaders();

    void make_command_stuff();

    void make_descriptor_pools();

    void load_assets();

    /**
     * @brief Main window
     *
     */
    GLFWwindow* window;

    /**
    * @brief Stores destructors!
    */
    std::deque<std::function<void(vk::Instance)>> instanceDeletionQueue;
    std::deque<std::function<void(vk::Device)>> deviceDeletionQueue;

    /**
    * @brief the main instance
    */
    vk::Instance instance;

    /**
    * @brief dynamic instance dispatcher
    */
    vk::detail::DispatchLoaderDynamic dldi;

    /**
    * @brief Debug messenger
    */
    vk::DebugUtilsMessengerEXT debugMessenger = nullptr;

    /**
     * @brief A physical device
     * 
     */
    vk::PhysicalDevice physicalDevice;

    /**
    * @brief Memory Allocators
    */
    std::unordered_map<AllocatorScope, mem::Allocator> allocators;

    /**
     * @brief An abstraction of the physical device
     * 
     */
    Device logicalDevice;

    /**
     * @brief Queues for work submission
     * 
     */
    vk::Queue graphicsQueue;

    /**
     * @brief Surface to present to
     * 
     */
    vk::SurfaceKHR surface;

    /**
     * @brief The engine's swapchain
     * 
     */
    Swapchain swapchain;

    /**
    * @brief Describes the basic shape of the descriptor set layout
    */
    std::unordered_map<DescriptorScope, vk::DescriptorSetLayout> descriptorSetLayouts;

    /**
    * @brief Describes the descriptor sets used by a pipeline
    */
    std::unordered_map<PipelineType, vk::PipelineLayout> pipelineLayouts;

    /**
    * @brief For allocating descriptor sets
    */
    std::unordered_map<DescriptorScope, vk::DescriptorPool> descriptorPools;

    /**
    * @brief descriptor sets for each frame. The renderer owns them as
    * they don't change on swapchain recreation.
    */
    std::array<std::unordered_map<DescriptorScope, vk::DescriptorSet>, 2> descriptorSets;

    /**
     * @brief Frames used for rendering
     * 
     */
    std::vector<Frame> frames;

    /**
     * @brief compute shader
     * 
     */
    std::unordered_map<PipelineType, vk::ShaderEXT> shaders;

    /**
    * @brief memory pool for command buffer allocation
    */
    vk::CommandPool commandPool;

    /**
    * @brief command buffer for random work
    */
    vk::CommandBuffer mainCommandBuffer;

    /**
    * @brief vertex buffer for rendering
    */
    Buffer vertexBuffer;

    double timeSinceLastRender;

    /**
    * @brief frame currently being rendered
    */
    uint32_t frameIndex = 0;

    double lastTime, currentTime;
    int numFrames;
    float frameTime;
};
/*---------------------------------------------------------------------------*/