#include "frame.h"
#include "memory.h"
#include "../vkImage/image.h"

vkUtil::SwapChainFrame::SwapChainFrame(vk::PhysicalDevice physicalDevice, vk::Device logicalDevice,
	uint32_t width, uint32_t height) {
}

void vkUtil::SwapChainFrame::make_descriptor_resources() {
	
	//Make any resources
	
}

void vkUtil::SwapChainFrame::record_write_operations() {

	/*
	typedef struct VkWriteDescriptorSet {
		VkStructureType                  sType;
		const void* pNext;
		VkDescriptorSet                  dstSet;
		uint32_t                         dstBinding;
		uint32_t                         dstArrayElement;
		uint32_t                         descriptorCount;
		VkDescriptorType                 descriptorType;
		const VkDescriptorImageInfo* pImageInfo;
		const VkDescriptorBufferInfo* pBufferInfo;
		const VkBufferView* pTexelBufferView;
	} VkWriteDescriptorSet;
	*/
	vk::WriteDescriptorSet cameraVectorWriteOp, colorBufferWriteOp, colorBufferReadOp;

	colorBufferWriteOp.dstSet = descriptorSet[pipelineType::RAYTRACE];
	colorBufferWriteOp.dstBinding = 0;
	colorBufferWriteOp.dstArrayElement = 0; //byte offset within binding for inline uniform blocks
	colorBufferWriteOp.descriptorCount = 1;
	colorBufferWriteOp.descriptorType = vk::DescriptorType::eStorageImage;
	colorBufferWriteOp.pImageInfo = &(colorBuffer->writeDescriptor);

	colorBufferReadOp.dstSet = descriptorSet[pipelineType::SCREEN];
	colorBufferReadOp.dstBinding = 0;
	colorBufferReadOp.dstArrayElement = 0; //byte offset within binding for inline uniform blocks
	colorBufferReadOp.descriptorCount = 1;
	colorBufferReadOp.descriptorType = vk::DescriptorType::eCombinedImageSampler;
	colorBufferReadOp.pImageInfo = &(colorBuffer->readDescriptor);

	logicalDevice.updateDescriptorSets({colorBufferWriteOp, colorBufferReadOp}, nullptr);

	writeOps = {};

}

void vkUtil::SwapChainFrame::write_descriptor_set() {

	logicalDevice.updateDescriptorSets(writeOps, nullptr);
}

void vkUtil::SwapChainFrame::destroy() {

	logicalDevice.destroyImageView(imageView);
	logicalDevice.destroyFramebuffer(framebuffer[pipelineType::SCREEN]);
	logicalDevice.destroyFence(inFlight);
	logicalDevice.destroySemaphore(imageAvailable);
	logicalDevice.destroySemaphore(renderFinished);
	delete colorBuffer;
}