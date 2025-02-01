#pragma once
#include <vulkan/vulkan.hpp>

/**
 * @brief Holds all the state used in one
 *  rendering/presentation operation.
 * 
 */
class Frame {
public:
    Frame(vk::Image image);

    vk::Image image;
};