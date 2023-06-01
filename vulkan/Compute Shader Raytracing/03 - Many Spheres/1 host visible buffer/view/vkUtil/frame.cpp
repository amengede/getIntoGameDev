#include "frame.h"
#include "memory.h"
#include "../vkImage/image.h"

vkUtil::SwapChainFrame::SwapChainFrame(vk::PhysicalDevice physicalDevice, vk::Device logicalDevice,
	uint32_t width, uint32_t height) {
}

void vkUtil::SwapChainFrame::make_descriptor_resources(vk::Device logicalDevice, vk::PhysicalDevice physicalDevice, size_t sphereSize) {
	
	colorBufferDescriptor.imageLayout = vk::ImageLayout::eGeneral;
	colorBufferDescriptor.imageView = imageView;
	colorBufferDescriptor.sampler = nullptr;

	vkUtil::BufferInputChunk input;
	input.logicalDevice = logicalDevice;
	input.memoryProperties = vk::MemoryPropertyFlagBits::eHostVisible | vk::MemoryPropertyFlagBits::eHostCoherent;
	input.physicalDevice = physicalDevice;
	input.size = sphereSize;
	input.usage = vk::BufferUsageFlagBits::eStorageBuffer;
	sphereBuffer = vkUtil::createBuffer(input);
	sphereBuffer.create_resources(logicalDevice);

	input.size = 64;
	input.usage = vk::BufferUsageFlagBits::eUniformBuffer;
	sceneBuffer = vkUtil::createBuffer(input);
	sceneBuffer.create_resources(logicalDevice);
	
}

void vkUtil::SwapChainFrame::record_write_operations() {

	vk::WriteDescriptorSet colorBufferOp, sphereBufferOp, sceneBufferOp;

	colorBufferOp.dstSet = descriptorSet[pipelineType::RAYTRACE];
	colorBufferOp.dstBinding = 0;
	colorBufferOp.dstArrayElement = 0; //byte offset within binding for inline uniform blocks
	colorBufferOp.descriptorCount = 1;
	colorBufferOp.descriptorType = vk::DescriptorType::eStorageImage;
	colorBufferOp.pImageInfo = &colorBufferDescriptor;

	sphereBufferOp.dstSet = descriptorSet[pipelineType::RAYTRACE];
	sphereBufferOp.dstBinding = 1;
	sphereBufferOp.dstArrayElement = 0; //byte offset within binding for inline uniform blocks
	sphereBufferOp.descriptorCount = 1;
	sphereBufferOp.descriptorType = vk::DescriptorType::eStorageBuffer;
	sphereBufferOp.pBufferInfo = &(sphereBuffer.descriptor);

	sceneBufferOp.dstSet = descriptorSet[pipelineType::RAYTRACE];
	sceneBufferOp.dstBinding = 2;
	sceneBufferOp.dstArrayElement = 0; //byte offset within binding for inline uniform blocks
	sceneBufferOp.descriptorCount = 1;
	sceneBufferOp.descriptorType = vk::DescriptorType::eUniformBuffer;
	sceneBufferOp.pBufferInfo = &(sceneBuffer.descriptor);

	writeOps = { colorBufferOp, sphereBufferOp, sceneBufferOp };
}

void vkUtil::SwapChainFrame::write_descriptor_set() {
	logicalDevice.updateDescriptorSets(writeOps, nullptr);
}

void vkUtil::SwapChainFrame::destroy() {

	logicalDevice.destroyImageView(imageView);
	logicalDevice.destroyFence(inFlight);
	logicalDevice.destroySemaphore(imageAvailable);
	logicalDevice.destroySemaphore(renderFinished);
	sphereBuffer.destroy(logicalDevice);
	sceneBuffer.destroy(logicalDevice);
}