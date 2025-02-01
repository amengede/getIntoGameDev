#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include <vma/vk_mem_alloc.h>

void copy(
	vk::Buffer srcBuffer, VmaAllocationInfo& srcInfo, 
	vk::Buffer dstBuffer, VmaAllocationInfo& dstInfo, 
	vk::Queue queue, vk::CommandBuffer commandBuffer);