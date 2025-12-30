#pragma once
#include <string>
#include <dxgi.h>
#include <dxgi1_6.h>
#include <directx/d3dx12.h>

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
    void print(LPCWSTR message);

    /**
     * @brief Attempt to print a message.
     *
     * @param message The string to print
     */
    void print(DXGI_ADAPTER_DESC1 adapterDescription);

private:
    /**
     * @brief whether the logger is enabled or not.
     *
     */
    bool enabled;
};