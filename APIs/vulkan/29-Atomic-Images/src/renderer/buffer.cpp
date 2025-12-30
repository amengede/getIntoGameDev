#include "buffer.h"
#include "../logging/logger.h"

StorageBuffer make_depth_buffer(VmaAllocator& allocator, 
	std::deque<std::function<void(VmaAllocator)>>& vmaDeletionQueue,
	vk::Extent2D size) {

	Logger* logger = Logger::get_logger();

	vk::BufferCreateInfo bufferInfo = {};
	bufferInfo.flags = vk::BufferCreateFlags();
	bufferInfo.size = size.width * size.height * sizeof(uint64_t);
	bufferInfo.usage = vk::BufferUsageFlagBits::eStorageBuffer;
	VkBufferCreateInfo bufferInfoHandle = bufferInfo;

	VmaAllocationCreateInfo allocationInfo = {};
	allocationInfo.flags = VMA_ALLOCATION_CREATE_STRATEGY_MIN_MEMORY_BIT;
	allocationInfo.usage = VMA_MEMORY_USAGE_AUTO;

	// Vertex buffer
	StorageBuffer mesh;
	VkBuffer bufferHandle;

	VmaAllocationInfo bufferAllocationInfo;

	vmaCreateBuffer(allocator, &bufferInfoHandle,
		&allocationInfo, &bufferHandle, &(mesh.allocation),
		&bufferAllocationInfo);
	vmaSetAllocationName(allocator, mesh.allocation, "Storage Buffer");
	vmaGetAllocationInfo(allocator, mesh.allocation, &bufferAllocationInfo);

	logger->log(bufferAllocationInfo);

	mesh.buffer = bufferHandle;

	vmaDeletionQueue.push_back([mesh](VmaAllocator allocator) {
		vmaDestroyBuffer(allocator, mesh.buffer, mesh.allocation);
		});

	mesh.descriptor.buffer = mesh.buffer;
	mesh.descriptor.offset = 0;// bufferAllocationInfo.offset;
	mesh.descriptor.range = bufferAllocationInfo.size;

	return mesh;
}

void copy(
	vk::Buffer srcBuffer, VmaAllocationInfo& srcInfo,
	vk::Buffer dstBuffer, VmaAllocationInfo& dstInfo,
	vk::Queue queue, vk::CommandBuffer commandBuffer) {

	// Copy from staging buffer to vertex buffer
	commandBuffer.reset();
	vk::CommandBufferBeginInfo beginInfo;
	beginInfo.flags = vk::CommandBufferUsageFlagBits::eOneTimeSubmit;
	commandBuffer.begin(beginInfo);

	vk::BufferCopy copyRegion;
	copyRegion.srcOffset = srcInfo.offset;
	copyRegion.dstOffset = dstInfo.offset;
	copyRegion.size = srcInfo.size;
	commandBuffer.copyBuffer(srcBuffer, dstBuffer, 1, &copyRegion);

	commandBuffer.end();

	vk::SubmitInfo submitInfo;
	submitInfo.commandBufferCount = 1;
	submitInfo.pCommandBuffers = &commandBuffer;
	queue.submit(1, &submitInfo, nullptr);
	queue.waitIdle();

}