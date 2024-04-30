#pragma once
#include "../../config.h"

namespace vkImage {

	/**
		Create a view of a vulkan image.
	*/
	vk::ImageView make_image_view(
		vk::Device logicalDevice, vk::Image image, vk::Format format,
		vk::ImageAspectFlags aspect);
}