#include "frame.h"
#include "image.h"
#include "synchronisation.h"
#include <iostream>

Frame::Frame(Swapchain& swapchain, vk::Device& logicalDevice,
	vk::ShaderEXT* shaders,
	vk::DispatchLoaderDynamic& dl,
	vk::CommandBuffer commandBuffer,
	vk::Queue& queue,
	std::deque<std::function<void(vk::Device)>>& deletionQueue,
	vk::DescriptorSet& clearDescriptorSet,
	vk::PipelineLayout& clearPipelineLayout,
	vk::DescriptorSet& rasterizeDescriptorSet,
	vk::PipelineLayout& rasterizePipelineLayout,
	VmaAllocator& allocator, Mesh* vertexBuffer):
		logicalDevice(logicalDevice),
		swapchain(swapchain), shaders(shaders), dl(dl), 
		clearDescriptorSet(clearDescriptorSet), 
		clearPipelineLayout(clearPipelineLayout),
		rasterizeDescriptorSet(rasterizeDescriptorSet), 
		rasterizePipelineLayout(rasterizePipelineLayout),
		allocator(allocator), queue(queue) {
   
	this->commandBuffer = commandBuffer;
	this->vertexBuffer = vertexBuffer;

	imageAquiredSemaphore = make_semaphore(logicalDevice, deletionQueue);
	renderFinishedSemaphore = make_semaphore(logicalDevice, deletionQueue);
	renderFinishedFence = make_fence(logicalDevice, deletionQueue);

	colorBuffer = new StorageImage(allocator, swapchain.extent, commandBuffer, 
		queue, logicalDevice, vmaDeletionQueue, deviceDeletionQueue);

	vk::WriteDescriptorSet colorBufferWriteOp, vertexBufferWriteOp;

	colorBufferWriteOp.dstSet = clearDescriptorSet;
	colorBufferWriteOp.dstBinding = 0;
	colorBufferWriteOp.dstArrayElement = 0;
	colorBufferWriteOp.descriptorCount = 1;
	colorBufferWriteOp.descriptorType = vk::DescriptorType::eStorageImage;
	colorBufferWriteOp.pImageInfo = &(colorBuffer->descriptor);

	vertexBufferWriteOp.dstSet = rasterizeDescriptorSet;
	vertexBufferWriteOp.dstBinding = 0;
	vertexBufferWriteOp.dstArrayElement = 0;
	vertexBufferWriteOp.descriptorCount = 1;
	vertexBufferWriteOp.descriptorType = vk::DescriptorType::eStorageBuffer;
	vertexBufferWriteOp.pBufferInfo = &(vertexBuffer->descriptor);

	vk::WriteDescriptorSet updates[2] = { colorBufferWriteOp, vertexBufferWriteOp };

	logicalDevice.updateDescriptorSets(2, updates, 0, nullptr);
}

void Frame::record_command_buffer(uint32_t imageIndex) {

	vk::DescriptorSet sets[2] = { clearDescriptorSet, rasterizeDescriptorSet };

	commandBuffer.reset();

	vk::CommandBufferBeginInfo beginInfo = {};
	commandBuffer.begin(beginInfo);

	// Transition the Storage image so the compute shader can write to it
	transition_image_layout(commandBuffer, colorBuffer->image,
		vk::ImageLayout::eUndefined, vk::ImageLayout::eGeneral,
		vk::AccessFlagBits::eNone, vk::AccessFlagBits::eMemoryWrite,
		vk::PipelineStageFlagBits::eTopOfPipe, vk::PipelineStageFlagBits::eComputeShader);

	// clear screen
	vk::ShaderStageFlagBits stage = vk::ShaderStageFlagBits::eCompute;
	commandBuffer.bindShadersEXT(1, &stage, &shaders[0], dl);
	commandBuffer.bindDescriptorSets(vk::PipelineBindPoint::eCompute, clearPipelineLayout, 0, 1, sets, 0, nullptr);
	uint32_t workgroupCount = (swapchain.extent.width * swapchain.extent.height + 63) / 64;
	commandBuffer.dispatch(workgroupCount, 1, 1);

	// Compute barrier
	transition_image_layout(commandBuffer, colorBuffer->image,
		vk::ImageLayout::eGeneral, vk::ImageLayout::eGeneral,
		vk::AccessFlagBits::eMemoryWrite, vk::AccessFlagBits::eMemoryWrite,
		vk::PipelineStageFlagBits::eComputeShader, vk::PipelineStageFlagBits::eComputeShader);

	// draw triangle
	commandBuffer.bindShadersEXT(1, &stage, &shaders[1], dl);
	commandBuffer.bindDescriptorSets(vk::PipelineBindPoint::eCompute, rasterizePipelineLayout, 0, 2, sets, 0, nullptr);
	workgroupCount = 1;
	commandBuffer.dispatch(workgroupCount, 1, 1);

	// Transition storage image so it can be copied to the swapchain
	transition_image_layout(commandBuffer, colorBuffer->image,
		vk::ImageLayout::eGeneral, vk::ImageLayout::eTransferSrcOptimal,
		vk::AccessFlagBits::eMemoryWrite, vk::AccessFlagBits::eNone,
		vk::PipelineStageFlagBits::eComputeShader, vk::PipelineStageFlagBits::eNone);

	// Transitin swapchain image so we can copy to it
	transition_image_layout(commandBuffer, swapchain.images[imageIndex],
		vk::ImageLayout::eUndefined, vk::ImageLayout::eTransferDstOptimal,
		vk::AccessFlagBits::eNone, vk::AccessFlagBits::eNone,
		vk::PipelineStageFlagBits::eNone, vk::PipelineStageFlagBits::eNone);

	// Copy!
	copy_image_to_image(commandBuffer, colorBuffer->image, swapchain.images[imageIndex],
		colorBuffer->extent, swapchain.extent);

	// Transition swapchain image so it can be presented on screen
	transition_image_layout(commandBuffer, swapchain.images[imageIndex],
		vk::ImageLayout::eTransferDstOptimal, vk::ImageLayout::ePresentSrcKHR,
		vk::AccessFlagBits::eNone, vk::AccessFlagBits::eNone,
		vk::PipelineStageFlagBits::eNone, vk::PipelineStageFlagBits::eNone);

	commandBuffer.end();
}

void Frame::free_resources() {

	queue.waitIdle();

	while (vmaDeletionQueue.size() > 0) {
		vmaDeletionQueue.back()(allocator);
		vmaDeletionQueue.pop_back();
	}

	while (deviceDeletionQueue.size() > 0) {
		deviceDeletionQueue.back()(logicalDevice);
		deviceDeletionQueue.pop_back();
	}
}