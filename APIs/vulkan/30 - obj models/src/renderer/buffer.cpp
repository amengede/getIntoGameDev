#include "buffer.h"
#include "../logging/logger.h"

Buffer make_buffer(mem::Allocator& allocator, size_t byteSize,
	vk::BufferUsageFlags usage, bool hostWrite, const char* name) {

	Logger* logger = Logger::get_logger();

	VkBuffer handle;
	VmaAllocation allocation;

	vk::BufferCreateInfo bufferInfo = {};
	bufferInfo.flags = vk::BufferCreateFlags();
	bufferInfo.size = byteSize;
	bufferInfo.usage = usage;
	VkBufferCreateInfo bufferInfoHandle = bufferInfo;

	VmaAllocationCreateInfo allocationCreateInfo = {};
	allocationCreateInfo.flags = VMA_ALLOCATION_CREATE_STRATEGY_BEST_FIT_BIT;
	if (hostWrite) {
		allocationCreateInfo.flags |= VMA_ALLOCATION_CREATE_HOST_ACCESS_SEQUENTIAL_WRITE_BIT;
	}
	allocationCreateInfo.usage = VMA_MEMORY_USAGE_AUTO;
	if (allocator.pool) {
		allocationCreateInfo.pool = allocator.pool;
	}

	VmaAllocationInfo allocationInfo;

	vmaCreateBuffer(allocator.allocator, &bufferInfoHandle,
		&allocationCreateInfo, &handle, &allocation,
		&allocationInfo);
	vmaSetAllocationName(allocator.allocator, allocation, name);
	vmaGetAllocationInfo(allocator.allocator, allocation, &allocationInfo);

	logger->print(allocationInfo);

	Buffer buffer;
	buffer.allocation = allocation;
	buffer.buffer = handle;

	return buffer;
}

Buffer make_depth_buffer(mem::Allocator& allocator, vk::Extent2D size) {

	size_t byteSize = size.width * size.height * sizeof(uint64_t);
	vk::BufferUsageFlags usage = vk::BufferUsageFlagBits::eStorageBuffer;
	bool hostWrite = false;
	Buffer depthBuffer = make_buffer(allocator, byteSize, usage, 
		hostWrite, "Depth Buffer");

	allocator.deletionQueue.push_back([depthBuffer](VmaAllocator allocator) {
		vmaDestroyBuffer(allocator, depthBuffer.buffer, depthBuffer.allocation);
	});

	VmaAllocationInfo allocationInfo;
	vmaGetAllocationInfo(allocator.allocator, depthBuffer.allocation, &allocationInfo);
	depthBuffer.descriptor.buffer = depthBuffer.buffer;
	depthBuffer.descriptor.offset = 0;
	depthBuffer.descriptor.range = allocationInfo.size;

	return depthBuffer;
}

Buffer make_ubo(mem::Allocator& allocator, size_t byteSize) {

	vk::BufferUsageFlags usage = vk::BufferUsageFlagBits::eUniformBuffer;
	bool hostWrite = true;
	Buffer ubo = make_buffer(allocator, byteSize, usage,
		hostWrite, "Uniform Buffer");

	allocator.deletionQueue.push_back([ubo](VmaAllocator allocator) {
		vmaDestroyBuffer(allocator, ubo.buffer, ubo.allocation);
		});

	VmaAllocationInfo allocationInfo;
	vmaGetAllocationInfo(allocator.allocator, ubo.allocation, &allocationInfo);
	ubo.descriptor.buffer = ubo.buffer;
	ubo.descriptor.offset = 0;
	ubo.descriptor.range = allocationInfo.size;

	return ubo;
}

void copy(VmaAllocator& allocator, Buffer& src, Buffer& dst,
	vk::Queue queue, vk::CommandBuffer commandBuffer) {

	VmaAllocationInfo srcInfo, dstInfo;
	vmaGetAllocationInfo(allocator, src.allocation, &srcInfo);
	vmaGetAllocationInfo(allocator, dst.allocation, &dstInfo);

	// Copy from staging buffer to vertex buffer
	commandBuffer.reset();
	vk::CommandBufferBeginInfo beginInfo;
	beginInfo.flags = vk::CommandBufferUsageFlagBits::eOneTimeSubmit;
	commandBuffer.begin(beginInfo);

	vk::BufferCopy copyRegion;
	copyRegion.srcOffset = srcInfo.offset;
	copyRegion.dstOffset = dstInfo.offset;
	copyRegion.size = srcInfo.size;
	commandBuffer.copyBuffer(src.buffer, dst.buffer, 1, &copyRegion);

	commandBuffer.end();

	vk::SubmitInfo submitInfo;
	submitInfo.commandBufferCount = 1;
	submitInfo.pCommandBuffers = &commandBuffer;
	queue.submit(1, &submitInfo, nullptr);
	queue.waitIdle();

}