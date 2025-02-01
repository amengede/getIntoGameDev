#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include <deque>
#include <functional>

/**
 * @brief Handy bundle of info describing
 *  what a surface can do.
 * 
 */
struct SurfaceDetails {
    /**
     * @brief no. of images and supported sizes
     * 
     */
	vk::SurfaceCapabilitiesKHR capabilities;

    /**
     * @brief supported pixel formats
     * 
     */
	std::vector<vk::SurfaceFormatKHR> formats;

    /**
     * @brief available presentation modes
     * 
     */
	std::vector<vk::PresentModeKHR> presentModes;
};

/**
 * @brief A swapchain.
 * 
 */
class Swapchain {
public:

    /**
     * @brief Construct a new Swapchain object
     * 
     * @param logicalDevice vulkan device
     * @param physicalDevice physical device
     * @param surface the window surface to present to
     * @param width requested swapchain width
     * @param height requested swapchain height
     * @param deviceDeletionQueue deletion queue
     */
    void build(
        vk::Device logicalDevice, 
        vk::PhysicalDevice physicalDevice, 
        vk::SurfaceKHR surface, 
        uint32_t width, uint32_t height,
        std::deque<std::function<void(vk::Device)>>& deviceDeletionQueue);

    /**
     * @brief the number of images
     * 
     */
    uint32_t imageCount;

    /**
     * @brief The underlying swapchain resource
     * 
     */
    vk::SwapchainKHR chain;

    /**
     * @brief image format
     * 
     */
    vk::SurfaceFormatKHR format;

    /**
     * @brief image size
     * 
     */
    vk::Extent2D extent;

private:

    /**
     * @brief Check the properties of a surface
     * 
     * @param physicalDevice the Physical Device
     * @param surface window surface
     * @return SurfaceDetails the support details
     */
    SurfaceDetails query_surface_support(
        vk::PhysicalDevice physicalDevice, vk::SurfaceKHR surface);

    /**
     * @brief Choose an extent, working within the given constraints
     * 
     * @param width requested width
     * @param height requested height
     * @param capabilities surface capability support
     * @return vk::Extent2D the chosen extent
     */
    vk::Extent2D choose_extent(uint32_t width, uint32_t height, 
        vk::SurfaceCapabilitiesKHR capabilities);

    /**
     * @brief Choose a present mode
     * 
     * @param presentModes available present modes
     * @return vk::PresentModeKHR the chosen present mode
     */
    vk::PresentModeKHR choose_present_mode(
        std::vector<vk::PresentModeKHR> presentModes);

    /**
     * @brief Choose a surface format
     * 
     * @param formats supported formats to choose from
     * @return vk::SurfaceFormatKHR the chosen format
     */
	vk::SurfaceFormatKHR choose_surface_format(
        std::vector<vk::SurfaceFormatKHR> formats);
};