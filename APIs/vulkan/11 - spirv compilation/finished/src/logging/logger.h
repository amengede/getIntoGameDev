#pragma once
#include <string>
#include <deque>
#include <functional>
#include <vulkan/vulkan.hpp>
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
     * @brief Get the logger object
     *
     * @return The logger.
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
     * @brief Returns the debug logger's status.
     *
     * @return Whether the debug logger is currently enabled.
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
    * @param version The raw version code.
    */
    void report_version_number(uint32_t version);

    /**
    * @brief Print a list of items
    * @param list An array of strings
    * @param count the number of strings to print
    */
    void print_list(const char** list, uint32_t count);

    /**
    * @brief Print a list of Vulkan extensions
    * @param extensions a vector of extensions
    */
    void print_extensions(std::vector<vk::ExtensionProperties>& extensions);

    /**
    * @brief Print a list of Vulkan layers
    * @param layers a vector of layers
    */
    void print_layers(std::vector<vk::LayerProperties>& layers);

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
        vk::Instance& instance, vk::DispatchLoaderDynamic& dldi, 
        std::deque<std::function<void(vk::Instance)>>& deletionQueue);

    /**
     * @brief Logs a description of the physical device.
     * 
     * @param device device to be described.
     */
    void log(const vk::PhysicalDevice& device);

    /**
     * @brief Logs a description of the queue families supported
     * by a device.
    */
    void log(const std::vector<vk::QueueFamilyProperties>& queueFamilies);

    /**
     * @brief Logs the capabilities of a surface.
     * 
     * @param capabilities The surface capabilities to report
     */
    void log(const vk::SurfaceCapabilitiesKHR& capabilities);

    /**
     * @brief Log a 2D extent
     * 
     * @param extent extent to report
     * @param prefix prefix string. default is single tab
     */
    void log(const vk::Extent2D& extent, const char* prefix = "\t");

    /**
     * @brief Log a vector of strings
     * 
     * @param items list to report
     * @param prefix prefix string. default is single tab
     */
    void log(const std::vector<std::string>& items, const char* prefix = "\t");

    /**
     * @brief log a set of surface formats
     * 
     * @param formats formats to report
     */
    void log(const std::vector<vk::SurfaceFormatKHR>& formats);

    /**
     * @brief log a set of present modes
     * 
     * @param modes present modes to report
     */
    void log(const std::vector<vk::PresentModeKHR>& modes);
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