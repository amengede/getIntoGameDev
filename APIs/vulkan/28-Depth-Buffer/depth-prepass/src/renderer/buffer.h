#pragma once
#define VULKAN_HPP_NO_EXCEPTIONS
#include <vulkan/vulkan.hpp>
#include <vma/vk_mem_alloc.h>
#include <deque>
#include <functional>

class StorageBuffer {
public:
	vk::Buffer buffer;
	VmaAllocation allocation;
	vk::DescriptorBufferInfo descriptor;
};

StorageBuffer make_depth_buffer(VmaAllocator& allocator, 
	std::deque<std::function<void(VmaAllocator)>>& vmaDeletionQueue, 
	vk::Extent2D size);

void copy(
	vk::Buffer srcBuffer, VmaAllocationInfo& srcInfo, 
	vk::Buffer dstBuffer, VmaAllocationInfo& dstInfo, 
	vk::Queue queue, vk::CommandBuffer commandBuffer);