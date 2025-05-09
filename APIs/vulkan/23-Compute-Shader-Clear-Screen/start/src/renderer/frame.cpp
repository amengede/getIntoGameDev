#include "frame.h"
#include "image.h"
#include "synchronisation.h"
#include <iostream>

Frame::Frame(Swapchain& swapchain, vk::Device& logicalDevice,
	vk::ShaderEXT& shader,
	vk::DispatchLoaderDynamic& dl,
	vk::CommandBuffer commandBuffer,
	vk::Queue& queue,
	std::deque<std::function<void(vk::Device)>>& deletionQueue,
	vk::DescriptorSet& descriptorSet,
	vk::PipelineLayout& pipelineLayout,
	VmaAllocator& allocator):
		logicalDevice(logicalDevice),
		swapchain(swapchain), shader(shader), dl(dl), 
		descriptorSet(descriptorSet), pipelineLayout(pipelineLayout),
		allocator(allocator), queue(queue) {
   
	this->commandBuffer = commandBuffer;

	imageAquiredSemaphore = make_semaphore(logicalDevice, deletionQueue);
	renderFinishedSemaphore = make_semaphore(logicalDevice, deletionQueue);
	renderFinishedFence = make_fence(logicalDevice, deletionQueue);

	colorBuffer = new StorageImage(allocator, swapchain.extent, commandBuffer, 
		queue, logicalDevice, vmaDeletionQueue, deviceDeletionQueue);
}

void Frame::record_command_buffer(uint32_t imageIndex) {

	commandBuffer.reset();

	vk::CommandBufferBeginInfo beginInfo = {};
	commandBuffer.begin(beginInfo);

	/*
	
	transition_image_layout(commandBuffer, swapchain.images[imageIndex],
		vk::ImageLayout::eUndefined, vk::ImageLayout::eAttachmentOptimal,
		vk::AccessFlagBits::eNone, vk::AccessFlagBits::eColorAttachmentWrite,
		vk::PipelineStageFlagBits::eTopOfPipe, vk::PipelineStageFlagBits::eColorAttachmentOutput);

	commandBuffer.beginRenderingKHR(renderingInfo, dl);

	vk::ShaderStageFlagBits stages[2] = {
		vk::ShaderStageFlagBits::eVertex,
		vk::ShaderStageFlagBits::eFragment
	};
	commandBuffer.bindShadersEXT(stages, shaders, dl);

	commandBuffer.bindVertexBuffers(0, 1, &(triangleMesh->buffer), &(triangleMesh->offset));

	commandBuffer.draw(3, 1, 0, 0);

	commandBuffer.endRenderingKHR(dl);

	transition_image_layout(commandBuffer, swapchain.images[imageIndex],
		vk::ImageLayout::eAttachmentOptimal, vk::ImageLayout::ePresentSrcKHR,
		vk::AccessFlagBits::eColorAttachmentWrite, vk::AccessFlagBits::eNone,
		vk::PipelineStageFlagBits::eColorAttachmentOutput, vk::PipelineStageFlagBits::eBottomOfPipe);
	*/

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