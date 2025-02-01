#include "frame.h"
#include "memory.h"
#include "../vkImage/image.h"

vkUtil::SwapChainFrame::SwapChainFrame(vk::PhysicalDevice physicalDevice, vk::Device logicalDevice,
	uint32_t width, uint32_t height) {
}

void vkUtil::SwapChainFrame::make_descriptor_resources() {
	
	colorBufferDescriptor.imageLayout = vk::ImageLayout::eGeneral;
	colorBufferDescriptor.imageView = imageView;
	colorBufferDescriptor.sampler = nullptr;
	
}

void vkUtil::SwapChainFrame::record_write_operations() {
	vk::WriteDescriptorSet colorBufferOp;

	colorBufferOp.dstSet = descriptorSet[pipelineType::RAYTRACE];
	colorBufferOp.dstBinding = 0;
	colorBufferOp.dstArrayElement = 0; //byte offset within binding for inline uniform blocks
	colorBufferOp.descriptorCount = 1;
	colorBufferOp.descriptorType = vk::DescriptorType::eStorageImage;
	colorBufferOp.pImageInfo = &colorBufferDescriptor;

	writeOps = { colorBufferOp };
}

void vkUtil::SwapChainFrame::write_descriptor_set() {
	logicalDevice.updateDescriptorSets(writeOps, nullptr);
}

void vkUtil::SwapChainFrame::destroy() {

	logicalDevice.destroyImageView(imageView);
	logicalDevice.destroyFence(inFlight);
	logicalDevice.destroySemaphore(imageAvailable);
	logicalDevice.destroySemaphore(renderFinished);
}