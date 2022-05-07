#pragma once

#include "../vk_types.h"
#include "../vk_engine.h"

namespace vkutil {

	void loadImage(VulkanEngine& engine, const char* filename, Image& outputImage);

	void generateMipMaps(VulkanEngine& engine, Image& image, VkFormat imageFormat, int32_t width, int32_t height);
}