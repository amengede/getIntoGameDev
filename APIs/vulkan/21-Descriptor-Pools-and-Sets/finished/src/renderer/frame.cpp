#include "frame.h"
#include "image.h"
#include "synchronisation.h"
#include <iostream>
#include "descriptors.h"

Frame::Frame(Swapchain& swapchain, vk::Device& logicalDevice,
	vk::ShaderEXT& shader,
	vk::DispatchLoaderDynamic& dl,
	vk::CommandBuffer commandBuffer,
	std::deque<std::function<void(vk::Device)>>& deletionQueue,
	vk::DescriptorSetLayout& descriptorSetLayout,
	vk::DescriptorPool& descriptorPool,
	vk::PipelineLayout& pipelineLayout):
		swapchain(swapchain), shader(shader), dl(dl), descriptorSetLayout(descriptorSetLayout), 
		descriptorPool(descriptorPool), pipelineLayout(pipelineLayout) {
   
	this->commandBuffer = commandBuffer;

	imageAquiredSemaphore = make_semaphore(logicalDevice, deletionQueue);
	renderFinishedSemaphore = make_semaphore(logicalDevice, deletionQueue);
	renderFinishedFence = make_fence(logicalDevice, deletionQueue);
	descriptorSet = allocate_descriptor_set(logicalDevice, descriptorPool, descriptorSetLayout);
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
