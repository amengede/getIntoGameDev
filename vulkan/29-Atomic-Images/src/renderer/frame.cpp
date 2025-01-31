#include "frame.h"
#include "image.h"
#include "synchronisation.h"
#include <iostream>

Frame::Frame(Swapchain& swapchain, vk::Device& logicalDevice,
	std::unordered_map<PipelineType, vk::ShaderEXT>& shaders,
	vk::DispatchLoaderDynamic& dl,
	vk::CommandBuffer commandBuffer,
	vk::Queue& queue,
	std::deque<std::function<void(vk::Device)>>& deletionQueue,
	std::unordered_map<DescriptorScope, vk::DescriptorSet>& descriptorSets,
	std::unordered_map<PipelineType, vk::PipelineLayout>& pipelineLayouts,
	VmaAllocator& allocator, StorageBuffer* vertexBuffer):
		logicalDevice(logicalDevice),
		swapchain(swapchain), shaders(shaders), dl(dl), 
		descriptorSets(descriptorSets), 
		pipelineLayouts(pipelineLayouts),
		allocator(allocator), queue(queue) {
   
	this->commandBuffer = commandBuffer;

	imageAquiredSemaphore = make_semaphore(logicalDevice, deletionQueue);
	renderFinishedSemaphore = make_semaphore(logicalDevice, deletionQueue);
	renderFinishedFence = make_fence(logicalDevice, deletionQueue);

	colorBuffer = new StorageImage(allocator, vk::Format::eR64Uint, swapchain.extent, commandBuffer, 
		queue, logicalDevice, vmaDeletionQueue, deviceDeletionQueue);
	tempSurface = new StorageImage(allocator, vk::Format::eR8G8B8A8Unorm, swapchain.extent, commandBuffer, 
		queue, logicalDevice, vmaDeletionQueue, deviceDeletionQueue);

	vk::WriteDescriptorSet colorBufferWriteOp, vertexBufferWriteOp, tempSurfaceWriteOp;

	colorBufferWriteOp.dstSet = descriptorSets[DescriptorScope::eFrame];
	colorBufferWriteOp.dstBinding = 0;
	colorBufferWriteOp.dstArrayElement = 0;
	colorBufferWriteOp.descriptorCount = 1;
	colorBufferWriteOp.descriptorType = vk::DescriptorType::eStorageImage;
	colorBufferWriteOp.pImageInfo = &(colorBuffer->descriptor);

	vertexBufferWriteOp.dstSet = descriptorSets[DescriptorScope::eDrawCall];
	vertexBufferWriteOp.dstBinding = 0;
	vertexBufferWriteOp.dstArrayElement = 0;
	vertexBufferWriteOp.descriptorCount = 1;
	vertexBufferWriteOp.descriptorType = vk::DescriptorType::eStorageBuffer;
	vertexBufferWriteOp.pBufferInfo = &(vertexBuffer->descriptor);

	tempSurfaceWriteOp.dstSet = descriptorSets[DescriptorScope::ePost];
	tempSurfaceWriteOp.dstBinding = 0;
	tempSurfaceWriteOp.dstArrayElement = 0;
	tempSurfaceWriteOp.descriptorCount = 1;
	tempSurfaceWriteOp.descriptorType = vk::DescriptorType::eStorageImage;
	tempSurfaceWriteOp.pImageInfo = &(tempSurface->descriptor);

	vk::WriteDescriptorSet updates[3] = { colorBufferWriteOp, vertexBufferWriteOp, tempSurfaceWriteOp };

	logicalDevice.updateDescriptorSets(3, updates, 0, nullptr);
}

void Frame::record_command_buffer(uint32_t imageIndex) {

	//bool smallTriangle = true;

	commandBuffer.reset();

	vk::CommandBufferBeginInfo beginInfo = {};
	commandBuffer.begin(beginInfo);

	// Transition the Storage image so the compute shader can write to it
	transition_image_layout(commandBuffer, colorBuffer->image,
		vk::ImageLayout::eUndefined, vk::ImageLayout::eGeneral,
		vk::AccessFlagBits::eNone, vk::AccessFlagBits::eMemoryWrite,
		vk::PipelineStageFlagBits::eTopOfPipe, vk::PipelineStageFlagBits::eComputeShader);

	// clear screen
	PipelineType pipelineType = PipelineType::eClear;
	vk::ShaderStageFlagBits stage = vk::ShaderStageFlagBits::eCompute;
	commandBuffer.bindShadersEXT(1, &stage, &shaders[pipelineType], dl);
	commandBuffer.bindDescriptorSets(vk::PipelineBindPoint::eCompute, pipelineLayouts[pipelineType],
		0, 1, &descriptorSets[DescriptorScope::eFrame], 0, nullptr);
	uint32_t workgroupCountX = (swapchain.extent.width + 7) / 8;
	uint32_t workgroupCountY = (swapchain.extent.height + 7) / 8;
	commandBuffer.dispatch(workgroupCountX, workgroupCountY, 1);

	// Compute barrier
	transition_image_layout(commandBuffer, colorBuffer->image,
		vk::ImageLayout::eGeneral, vk::ImageLayout::eGeneral,
		vk::AccessFlagBits::eMemoryWrite, vk::AccessFlagBits::eMemoryWrite,
		vk::PipelineStageFlagBits::eComputeShader, vk::PipelineStageFlagBits::eComputeShader);

	// draw triangles
	// Big triangle
	pipelineType = PipelineType::eRasterizeBig;
	commandBuffer.bindShadersEXT(1, &stage, &shaders[pipelineType], dl);
	commandBuffer.bindDescriptorSets(vk::PipelineBindPoint::eCompute, pipelineLayouts[pipelineType],
		0, 1, &descriptorSets[DescriptorScope::eFrame], 0, nullptr);
	commandBuffer.bindDescriptorSets(vk::PipelineBindPoint::eCompute, pipelineLayouts[pipelineType],
		1, 1, &descriptorSets[DescriptorScope::eDrawCall], 0, nullptr);
	workgroupCountX = (static_cast<uint32_t>(0.9f * 400) + 7) / 8;
	workgroupCountY = (static_cast<uint32_t>(0.6f * 300) + 7) / 8;
	commandBuffer.dispatch(workgroupCountX, workgroupCountY, 1);
	// Small triangles
	pipelineType = PipelineType::eRasterizeSmall;
	commandBuffer.bindShadersEXT(1, &stage, &shaders[pipelineType], dl);
	commandBuffer.bindDescriptorSets(vk::PipelineBindPoint::eCompute, pipelineLayouts[pipelineType],
		0, 1, &descriptorSets[DescriptorScope::eFrame], 0, nullptr);
	commandBuffer.bindDescriptorSets(vk::PipelineBindPoint::eCompute, pipelineLayouts[pipelineType],
		1, 1, &descriptorSets[DescriptorScope::eDrawCall], 0, nullptr);
	uint32_t workgroupCount = 1;
	commandBuffer.dispatch(workgroupCount, 1, 1);

	// Prepare Temp Surface for writing
	transition_image_layout(commandBuffer, tempSurface->image,
		vk::ImageLayout::eUndefined, vk::ImageLayout::eGeneral,
		vk::AccessFlagBits::eMemoryWrite, vk::AccessFlagBits::eMemoryWrite,
		vk::PipelineStageFlagBits::eComputeShader, vk::PipelineStageFlagBits::eComputeShader);
	
	// Extract color info from color buffer
	pipelineType = PipelineType::eWriteColor;
	commandBuffer.bindShadersEXT(1, &stage, &shaders[pipelineType], dl);
	commandBuffer.bindDescriptorSets(vk::PipelineBindPoint::eCompute, pipelineLayouts[pipelineType],
		0, 1, &descriptorSets[DescriptorScope::eFrame], 0, nullptr);
	commandBuffer.bindDescriptorSets(vk::PipelineBindPoint::eCompute, pipelineLayouts[pipelineType],
		1, 1, &descriptorSets[DescriptorScope::ePost], 0, nullptr);
	workgroupCountX = (swapchain.extent.width + 7) / 8;
	workgroupCountY = (swapchain.extent.height + 7) / 8;
	commandBuffer.dispatch(workgroupCountX, workgroupCountY, 1);

	// Transition storage image so it can be copied to the swapchain
	transition_image_layout(commandBuffer, tempSurface->image,
		vk::ImageLayout::eGeneral, vk::ImageLayout::eTransferSrcOptimal,
		vk::AccessFlagBits::eMemoryWrite, vk::AccessFlagBits::eNone,
		vk::PipelineStageFlagBits::eComputeShader, vk::PipelineStageFlagBits::eNone);

	// Transitin swapchain image so we can copy to it
	transition_image_layout(commandBuffer, swapchain.images[imageIndex],
		vk::ImageLayout::eUndefined, vk::ImageLayout::eTransferDstOptimal,
		vk::AccessFlagBits::eNone, vk::AccessFlagBits::eNone,
		vk::PipelineStageFlagBits::eNone, vk::PipelineStageFlagBits::eNone);

	// Copy!
	copy_image_to_image(commandBuffer, tempSurface->image, swapchain.images[imageIndex],
		tempSurface->extent, swapchain.extent);

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