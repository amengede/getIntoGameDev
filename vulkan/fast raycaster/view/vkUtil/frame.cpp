#include "frame.h"
#include "memory.h"

vkUtil::SwapChainFrame::SwapChainFrame(vk::PhysicalDevice physicalDevice, vk::Device logicalDevice,
	uint32_t width, uint32_t height):
physicalDevice(physicalDevice), logicalDevice(logicalDevice), width(width), height(height){
}

void vkUtil::SwapChainFrame::make_descriptor_resources() {

	//Color Buffer Descriptor
	colorBufferDescriptor.imageLayout = vk::ImageLayout::eGeneral;
	colorBufferDescriptor.imageView = imageView;
	colorBufferDescriptor.sampler = nullptr;

	//Set up wall buffer
	BufferInputChunk input;
	input.logicalDevice = logicalDevice;
	input.physicalDevice = physicalDevice;
	input.memoryProperties = vk::MemoryPropertyFlagBits::eHostCoherent | vk::MemoryPropertyFlagBits::eHostVisible;
	input.usage = vk::BufferUsageFlagBits::eStorageBuffer;
	input.size = 1024 * 48;
	wallBuffer = vkUtil::createBuffer(input);
	wallBuffer.create_resources(logicalDevice);

	//Set up camera buffer
	input.size = 32;
	input.usage = vk::BufferUsageFlagBits::eUniformBuffer;
	cameraBuffer = vkUtil::createBuffer(input);
	cameraBuffer.create_resources(logicalDevice);

}

void vkUtil::SwapChainFrame::record_write_operations() {

	vk::WriteDescriptorSet colorBufferOp, sphereBufferOp, sceneBufferOp;

	colorBufferOp.dstSet = descriptorSet;
	colorBufferOp.dstBinding = 0;
	colorBufferOp.dstArrayElement = 0; //byte offset within binding for inline uniform blocks
	colorBufferOp.descriptorCount = 1;
	colorBufferOp.descriptorType = vk::DescriptorType::eStorageImage;
	colorBufferOp.pImageInfo = &colorBufferDescriptor;

	sphereBufferOp.dstSet = descriptorSet;
	sphereBufferOp.dstBinding = 1;
	sphereBufferOp.dstArrayElement = 0; //byte offset within binding for inline uniform blocks
	sphereBufferOp.descriptorCount = 1;
	sphereBufferOp.descriptorType = vk::DescriptorType::eStorageBuffer;
	sphereBufferOp.pBufferInfo = &(wallBuffer.descriptor);

	sceneBufferOp.dstSet = descriptorSet;
	sceneBufferOp.dstBinding = 2;
	sceneBufferOp.dstArrayElement = 0; //byte offset within binding for inline uniform blocks
	sceneBufferOp.descriptorCount = 1;
	sceneBufferOp.descriptorType = vk::DescriptorType::eUniformBuffer;
	sceneBufferOp.pBufferInfo = &(cameraBuffer.descriptor);

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
	wallBuffer.destroy(logicalDevice);
	cameraBuffer.destroy(logicalDevice);
}