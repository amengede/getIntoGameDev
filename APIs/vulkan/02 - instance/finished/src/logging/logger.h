#pragma once
#include <string>
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

private:
    /**
     * @brief whether the logger is enabled or not.
     *
     */
    bool enabled;
};