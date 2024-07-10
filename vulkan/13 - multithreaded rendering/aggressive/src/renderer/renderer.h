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
#include <taskflow/taskflow.hpp>

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
     * @brief An abstraction of the physical device
     * 
     */
    vk::Device logicalDevice;

    /**
     * @brief Queues for work submission
     * 
     */
    vk::Queue graphicsQueues[4];

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
     * @brief Frames used for rendering.
     * Each frame represents the whole state of
     * the program at every stage of the
     * "Upload - Render - Present" instruction pipeline
     * 
     */
    std::vector<Frame> frames;

    /**
     * @brief shader objects
     * 
     */
    std::vector<vk::ShaderEXT> shaders;

    /**
    * @brief memory pool for command buffer allocation
    */
    vk::CommandPool commandPool;

    /**
    * @brief Rendering info
    */
    vk::RenderingInfoKHR renderingInfo;

    /**
    * @brief used for stepping through the instruction pipeline
    */
    uint32_t currentFrame = 0;

    /**
    * @brief for executing task graphs
    */
    tf::Executor executor;

    /**
    * @brief stores "prebaked" pipeline executions
    */
    tf::Taskflow drawingJobs[4];

    double lastTime, currentTime;
    int numFrames;
    float frameTime;

    void make_drawing_instruction_pipeline();
};