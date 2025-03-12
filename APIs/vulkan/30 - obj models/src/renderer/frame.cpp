#include "frame.h"
#include "image.h"
#include "synchronisation.h"
#include <sstream>
#include <string>
#include "../backend/memory.h"
#include "../logging/logger.h"
#include "../math/math.h"

Frame::Frame(Swapchain& swapchain, Device& logicalDevice,
	std::unordered_map<PipelineType, vk::ShaderEXT>& shaders,
	vk::detail::DispatchLoaderDynamic& dl,
	vk::CommandBuffer commandBuffer,
	vk::Queue& queue,
	std::unordered_map<DescriptorScope, vk::DescriptorSet>& descriptorSets,
	std::unordered_map<PipelineType, vk::PipelineLayout>& pipelineLayouts,
	Buffer* vertexBuffer,
	std::unordered_map<AllocatorScope, mem::Allocator>& allocators,
	int frameNumber) :
		swapchain(swapchain), shaders(shaders), dl(dl), 
		descriptorSets(descriptorSets), 
		pipelineLayouts(pipelineLayouts), queue(queue),
		allocators(allocators) {

	this->logicalDevice.device = logicalDevice.device;
   
	this->commandBuffer = commandBuffer;
	this->frameNumber = frameNumber;

	this->vertexBuffer = vertexBuffer;

	mem::Allocator& allocator = allocators[AllocatorScope::eProgram];
	UBO = make_ubo(allocator, sizeof(Bundle));

	Bundle ubo;
	ubo.proj = make_perspective_projection(45.0f, 4.0f / 3.0f, 0.1f, 100.0f);
	ubo.triCount[0] = vertexBuffer->triangleCount;

	void* dst;
	vmaMapMemory(allocator.allocator, UBO.allocation, &dst);
	memcpy(dst, &ubo, sizeof(Bundle));
	vmaUnmapMemory(allocator.allocator, UBO.allocation);

	build(vertexBuffer);
}

void Frame::record_command_buffer(uint32_t imageIndex) {

	commandBuffer.reset();

	vk::CommandBufferBeginInfo beginInfo = {};
	commandBuffer.begin(beginInfo);

	// Transition the Depth/Color buffer so the compute shader can write to it
	transition_image_layout(commandBuffer, depthColorBuffer->image,
		vk::ImageLayout::eUndefined, vk::ImageLayout::eGeneral,
		vk::AccessFlagBits::eNone, vk::AccessFlagBits::eMemoryWrite,
		vk::PipelineStageFlagBits::eTopOfPipe,
		vk::PipelineStageFlagBits::eComputeShader);

	clear_screen();

	//draw_big_triangle();

	draw_small_triangles();

	// Prepare Color buffer for writing
	transition_image_layout(commandBuffer, colorBuffer->image,
		vk::ImageLayout::eUndefined, vk::ImageLayout::eGeneral,
		vk::AccessFlagBits::eMemoryWrite, vk::AccessFlagBits::eMemoryWrite,
		vk::PipelineStageFlagBits::eComputeShader,
		vk::PipelineStageFlagBits::eComputeShader);
	
	resolve_to_color_buffer();

	// Transition color buffer so it can be copied to the swapchain
	transition_image_layout(commandBuffer, colorBuffer->image,
		vk::ImageLayout::eGeneral, vk::ImageLayout::eTransferSrcOptimal,
		vk::AccessFlagBits::eMemoryWrite, vk::AccessFlagBits::eNone,
		vk::PipelineStageFlagBits::eComputeShader,
		vk::PipelineStageFlagBits::eNone);

	// Transitin swapchain image so we can copy to it
	transition_image_layout(commandBuffer, swapchain.images[imageIndex],
		vk::ImageLayout::eUndefined, vk::ImageLayout::eTransferDstOptimal,
		vk::AccessFlagBits::eNone, vk::AccessFlagBits::eNone,
		vk::PipelineStageFlagBits::eNone, vk::PipelineStageFlagBits::eNone);

	// Copy!
	copy_image_to_image(commandBuffer, colorBuffer->image,
		swapchain.images[imageIndex], colorBuffer->extent, swapchain.extent);

	// Transition swapchain image so it can be presented on screen
	transition_image_layout(commandBuffer, swapchain.images[imageIndex],
		vk::ImageLayout::eTransferDstOptimal, vk::ImageLayout::ePresentSrcKHR,
		vk::AccessFlagBits::eNone, vk::AccessFlagBits::eNone,
		vk::PipelineStageFlagBits::eNone, vk::PipelineStageFlagBits::eNone);

	commandBuffer.end();
}

void Frame::clear_screen() {

	constexpr PipelineType pipelineType = PipelineType::eClear;
	constexpr vk::ShaderStageFlagBits stage = vk::ShaderStageFlagBits::eCompute;
	constexpr uint32_t stageCount = 1;
	vk::ShaderEXT* pShader = &shaders[pipelineType];
	commandBuffer.bindShadersEXT(stageCount, &stage, pShader, dl);

	constexpr uint32_t firstSet = 0;
	constexpr uint32_t setCount = 1;
	constexpr vk::PipelineBindPoint bindPoint = vk::PipelineBindPoint::eCompute;
	vk::PipelineLayout pipelineLayout = pipelineLayouts[pipelineType];
	vk::DescriptorSet* pDescriptorSet = &descriptorSets[DescriptorScope::eFrame];
	constexpr uint32_t dynamicOffsetCount = 0;
	constexpr uint32_t* pDynamicOffsets = nullptr;
	commandBuffer.bindDescriptorSets(bindPoint, pipelineLayout,
		firstSet, setCount, pDescriptorSet,
		dynamicOffsetCount, pDynamicOffsets);

	uint32_t workgroupCountX = (swapchain.extent.width + 7) / 8;
	uint32_t workgroupCountY = (swapchain.extent.height + 7) / 8;
	constexpr uint32_t workgroupCountZ = 1;
	commandBuffer.dispatch(workgroupCountX, workgroupCountY, workgroupCountZ);
}

void Frame::draw_big_triangle() {
	
	constexpr PipelineType pipelineType = PipelineType::eRasterizeBig;
	constexpr uint32_t stageCount = 1;
	constexpr vk::ShaderStageFlagBits stage = vk::ShaderStageFlagBits::eCompute;
	uint32_t firstSet = 0;
	constexpr uint32_t setCount = 1;
	vk::ShaderEXT* pShader = &shaders[pipelineType];
	commandBuffer.bindShadersEXT(stageCount, &stage, pShader, dl);

	constexpr vk::PipelineBindPoint bindPoint = vk::PipelineBindPoint::eCompute;
	vk::PipelineLayout pipelineLayout = pipelineLayouts[pipelineType];
	vk::DescriptorSet* pDescriptorSet = &descriptorSets[DescriptorScope::eFrame];
	constexpr uint32_t dynamicOffsetCount = 0;
	constexpr uint32_t* pDynamicOffsets = nullptr;
	commandBuffer.bindDescriptorSets(bindPoint, pipelineLayout,
		firstSet, setCount,
		pDescriptorSet, dynamicOffsetCount, pDynamicOffsets);
	
	firstSet = 1;
	pDescriptorSet = &descriptorSets[DescriptorScope::eDrawCall];
	commandBuffer.bindDescriptorSets(bindPoint, pipelineLayout,
		firstSet, setCount,
		pDescriptorSet, dynamicOffsetCount, pDynamicOffsets);

	uint32_t workgroupCountX = (static_cast<uint32_t>(0.9f * swapchain.extent.width) + 7) / 8;
	uint32_t workgroupCountY = (static_cast<uint32_t>(0.6f * swapchain.extent.height) + 7) / 8;
	constexpr uint32_t workgroupCountZ = 1;
	commandBuffer.dispatch(workgroupCountX, workgroupCountY, workgroupCountZ);
}

void Frame::draw_small_triangles() {

	constexpr uint32_t stageCount = 1;
	constexpr vk::ShaderStageFlagBits stage = vk::ShaderStageFlagBits::eCompute;
	constexpr PipelineType pipelineType = PipelineType::eRasterizeSmall;
	vk::ShaderEXT* pShader = &shaders[pipelineType];
	commandBuffer.bindShadersEXT(stageCount, &stage, pShader, dl);

	constexpr vk::PipelineBindPoint bindPoint = vk::PipelineBindPoint::eCompute;
	vk::PipelineLayout pipelineLayout = pipelineLayouts[pipelineType];
	uint32_t firstSet = 0;
	constexpr uint32_t setCount = 1;
	vk::DescriptorSet* pDescriptorSet = &descriptorSets[DescriptorScope::eFrame];
	constexpr uint32_t dynamicOffsetCount = 0;
	constexpr uint32_t* pDynamicOffsets = nullptr;
	commandBuffer.bindDescriptorSets(bindPoint, pipelineLayout, 
		firstSet, setCount, pDescriptorSet,
		dynamicOffsetCount, pDynamicOffsets);

	firstSet = 1;
	pDescriptorSet = &descriptorSets[DescriptorScope::eDrawCall];
	commandBuffer.bindDescriptorSets(bindPoint, pipelineLayout, 
		firstSet, setCount, pDescriptorSet,
		dynamicOffsetCount, pDynamicOffsets);

	uint32_t workgroupCountX = (vertexBuffer->triangleCount + 63) / 64;
	constexpr uint32_t workgroupCountY = 1;
	constexpr uint32_t workgroupCountZ = 1;
	commandBuffer.dispatch(workgroupCountX, workgroupCountY, workgroupCountZ);
}

void Frame::resolve_to_color_buffer() {

	constexpr PipelineType pipelineType = PipelineType::eWriteColor;
	constexpr uint32_t stageCount = 1;
	constexpr vk::ShaderStageFlagBits stage = vk::ShaderStageFlagBits::eCompute;
	vk::ShaderEXT* pShader = &shaders[pipelineType];
	commandBuffer.bindShadersEXT(stageCount, &stage, pShader, dl);

	constexpr vk::PipelineBindPoint bindPoint = vk::PipelineBindPoint::eCompute;
	vk::PipelineLayout pipelineLayout = pipelineLayouts[pipelineType];
	uint32_t firstSet = 0;
	constexpr uint32_t setCount = 1;
	vk::DescriptorSet* pDescriptorSet = &descriptorSets[DescriptorScope::eFrame];
	constexpr uint32_t dynamicOffsetCount = 0;
	constexpr uint32_t* pDynamicOffsets = nullptr;
	commandBuffer.bindDescriptorSets(bindPoint,
		pipelineLayout, firstSet, setCount,
		pDescriptorSet, dynamicOffsetCount, pDynamicOffsets);

	firstSet = 1;
	pDescriptorSet = &descriptorSets[DescriptorScope::ePost];
	commandBuffer.bindDescriptorSets(bindPoint,
		pipelineLayout, firstSet, setCount,
		pDescriptorSet, dynamicOffsetCount, pDynamicOffsets);

	uint32_t workgroupCountX = (swapchain.extent.width + 7) / 8;
	uint32_t workgroupCountY = (swapchain.extent.height + 7) / 8;
	constexpr uint32_t workgroupCountZ = 1;
	commandBuffer.dispatch(workgroupCountX, workgroupCountY, workgroupCountZ);
}

void Frame::free_resources(AllocatorScope scope) {

	if (depthColorBuffer) {
		delete depthColorBuffer;
		delete colorBuffer;
		depthColorBuffer = nullptr;
	}
}

void Frame::rebuild(Buffer* vertexBuffer) {

	free_resources(AllocatorScope::eFrame);

	build(vertexBuffer);
}

void Frame::build(Buffer* vertexBuffer) {

	queue.waitIdle();

	imageAquiredSemaphore = make_semaphore(logicalDevice);
	renderFinishedSemaphore = make_semaphore(logicalDevice);
	renderFinishedFence = make_fence(logicalDevice);

	std::stringstream nameBuilder;
	std::string name;

	nameBuilder << "Depth and Color Buffer (frame " << frameNumber << ")";
	name = nameBuilder.str();
	nameBuilder.str("");
	depthColorBuffer = new StorageImage(allocators[AllocatorScope::eFrame],
		vk::Format::eR64Uint,
		swapchain.extent, commandBuffer, queue, logicalDevice, name.c_str());

	nameBuilder << "Color Buffer (frame " << frameNumber << ")";
	name = nameBuilder.str();
	nameBuilder.str("");
	colorBuffer = new StorageImage(allocators[AllocatorScope::eFrame],
		vk::Format::eR8G8B8A8Unorm,
		swapchain.extent, commandBuffer, queue, logicalDevice, name.c_str());

	vk::WriteDescriptorSet colorBufferWriteOp, vertexBufferWriteOp, 
		uboWriteOp, tempSurfaceWriteOp;

	colorBufferWriteOp.dstSet = descriptorSets[DescriptorScope::eFrame];
	colorBufferWriteOp.dstBinding = 0;
	colorBufferWriteOp.dstArrayElement = 0;
	colorBufferWriteOp.descriptorCount = 1;
	colorBufferWriteOp.descriptorType = vk::DescriptorType::eStorageImage;
	colorBufferWriteOp.pImageInfo = &(depthColorBuffer->descriptor);

	vertexBufferWriteOp.dstSet = descriptorSets[DescriptorScope::eDrawCall];
	vertexBufferWriteOp.dstBinding = 0;
	vertexBufferWriteOp.dstArrayElement = 0;
	vertexBufferWriteOp.descriptorCount = 1;
	vertexBufferWriteOp.descriptorType = vk::DescriptorType::eStorageBuffer;
	vertexBufferWriteOp.pBufferInfo = &(vertexBuffer->descriptor);

	uboWriteOp.dstSet = descriptorSets[DescriptorScope::eDrawCall];
	uboWriteOp.dstBinding = 1;
	uboWriteOp.dstArrayElement = 0;
	uboWriteOp.descriptorCount = 1;
	uboWriteOp.descriptorType = vk::DescriptorType::eUniformBuffer;
	uboWriteOp.pBufferInfo = &(UBO.descriptor);

	tempSurfaceWriteOp.dstSet = descriptorSets[DescriptorScope::ePost];
	tempSurfaceWriteOp.dstBinding = 0;
	tempSurfaceWriteOp.dstArrayElement = 0;
	tempSurfaceWriteOp.descriptorCount = 1;
	tempSurfaceWriteOp.descriptorType = vk::DescriptorType::eStorageImage;
	tempSurfaceWriteOp.pImageInfo = &(colorBuffer->descriptor);

	vk::WriteDescriptorSet updates[4] = {
		colorBufferWriteOp, vertexBufferWriteOp,
		uboWriteOp, tempSurfaceWriteOp };

	logicalDevice.device.updateDescriptorSets(4, updates, 0, nullptr);
}