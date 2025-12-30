/*---------------------------------------------------------------------------*/
/*  Logging Functions
/*---------------------------------------------------------------------------*/
#pragma once
#include <string>
#include <deque>
#include <functional>
#include <vulkan/vulkan.hpp>
#include <vma/vk_mem_alloc.h>
#include "../backend/dynamic_array.h"
/**
    Handles messages to print.
*/
class Logger {
public:

    /**
     * @brief The instance of the logger.
     */
    static Logger* logger;

    /**
     * @returns The logger.
     */
    static Logger* get_logger();

    /**
     * @brief Set the logging mode
     *
     * @param mode: whether to enable (true) or disable (false)
     *  the logger.
     */
    void set_mode(bool mode);

    /**
     *
     * @returns Whether the debug logger is currently enabled.
     */
    bool is_enabled();

    /**
     * @brief Attempt to print a message.
     *
     * @param message The string to print
     */
    void print(std::string message);

    /**
    * @brief Extract and report the Vulkan version number.
    * 
    * @param version The raw version code.
    */
    void report_version_number(uint32_t version);

    /**
    * @brief Print a list of strings
    * 
    * @param list An array of strings
    * @param count the number of strings to print
    */
    void print(DynamicArray<const char*> list);

    /**
    * @brief Print a list of Vulkan extensions
    */
    void print(DynamicArray<vk::ExtensionProperties>& extensions);

    /**
    * @brief Print a list of Vulkan layers
    */
    void print(DynamicArray<vk::LayerProperties>& layers);

    /**
    * @brief Make a debug messenger
    *
    * @param instance The Vulkan instance which will be debugged.
    * @param dldi dynamically loads instance based dispatch functions
    * @param deletionQueue stores destructors
    * 
    * @return the created messenger
    */
    vk::DebugUtilsMessengerEXT make_debug_messenger(
        vk::Instance& instance, vk::detail::DispatchLoaderDynamic& dldi, 
        std::deque<std::function<void(vk::Instance)>>& deletionQueue);

    /**
     * @brief Prints a description of the physical device.
     * 
     * @param device device to be described.
     */
    void print(const vk::PhysicalDevice& device);

    /**
     * @brief Prints a description of the queue families supported
     * by a device.
    */
    void print(const DynamicArray<vk::QueueFamilyProperties>& queueFamilies);

    /**
     * @brief Prints the capabilities of a surface.
     */
    void print(const vk::SurfaceCapabilitiesKHR& capabilities);

    /**
     * @brief Print a 2D extent
     * 
     * @param extent extent to report
     * @param prefix prefix string. default is single tab
     */
    void print(const vk::Extent2D& extent, const char* prefix = "\t");

    /**
     * @brief Print a vector of strings
     * 
     * @param items list to report
     * @param prefix prefix string. default is single tab
     */
    void print(const DynamicArray<std::string>& items, const char* prefix = "\t");

    /**
     * @brief Print a set of surface formats
     */
    void print(const DynamicArray<vk::SurfaceFormatKHR>& formats);

    /**
     * @brief Print a set of present modes
     */
    void print(const DynamicArray<vk::PresentModeKHR>& modes);

    /**
    * @brief Print a VMA allocation
    */
    void print(const VmaAllocationInfo& allocationInfo);

    /**
    * @brief Print out some memory requirements
    */
    void print(const vk::MemoryRequirements& memoryRequriements);

private:
    /**
     * @brief whether the logger is enabled or not.
     *
     */
    bool enabled;
};

/**
* @brief Logging callback function.
*
* @param messageSeverity describes the severity level of the message
* @param messageType describes the type of the message
* @param pCallbackData standard data associated with the message
* @param pUserData custom extra data which can be associated with the message
*
* @return whether to end program execution
*/
VKAPI_ATTR VkBool32 VKAPI_CALL debugCallback(
    VkDebugUtilsMessageSeverityFlagBitsEXT messageSeverity,
    VkDebugUtilsMessageTypeFlagsEXT messageType,
    const VkDebugUtilsMessengerCallbackDataEXT* pCallbackData,
    void* pUserData);
/*---------------------------------------------------------------------------*/