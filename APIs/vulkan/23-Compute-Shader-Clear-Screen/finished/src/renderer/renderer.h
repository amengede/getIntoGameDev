#pragma once
#define GLFW_INCLUDE_VULKAN
#include <GLFW/glfw3.h>
#include <deque>
#include <functional>
#include "instance.h"
#include "../logging/logger.h"
#include "frame.h"
#include "swapchain.h"
#include <vector>
#include <vma/vk_mem_alloc.h>
#include "../factories/mesh_factory.h"

/**
 * @brief Vroom vroom.
 *
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
     *
     */
    ~Engine();

    /**
    * @brief draw something!
    */
    void draw();

    void update_timing();

private:

    /**
     * @brief static debug logger
     *
     */
    Logger* logger{ Logger::get_logger() };

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
    std::deque<std::function<void(VmaAllocator)>> vmaDeletionQueue;

    /**
    * @brief the main instance
    */
    vk::Instance instance;

    /**
    * @brief dynamic instance dispatcher
    */
    vk::DispatchLoaderDynamic dldi;

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
    * @brief Allocates memory for vulkan objects
    * 
    */
    VmaAllocator allocator;

    /**
     * @brief An abstraction of the physical device
     * 
     */
    vk::Device logicalDevice;

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
    vk::DescriptorSetLayout descriptorSetLayout;

    /**
    * @brief Describes the descriptor sets used by a pipeline
    */
    vk::PipelineLayout pipelineLayout;

    /**
    * @brief For allocating descriptor sets
    */
    vk::DescriptorPool descriptorPool;

    /**
    * @brief descriptor sets for each frame. The renderer owns them as
    * they don't change on swapchain recreation.
    */
    vk::DescriptorSet descriptorSets[2];

    /**
     * @brief Frames used for rendering
     * 
     */
    std::vector<Frame> frames;

    /**
     * @brief compute shader
     * 
     */
    vk::ShaderEXT shader;

    /**
    * @brief memory pool for command buffer allocation
    */
    vk::CommandPool commandPool;
    vk::CommandBuffer mainCommandBuffer;

    double lastTime, currentTime;
    int numFrames;
    float frameTime;

    uint32_t frameIndex = 0;
};