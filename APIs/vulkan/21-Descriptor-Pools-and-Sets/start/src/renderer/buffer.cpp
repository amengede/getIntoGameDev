#include "buffer.h"

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