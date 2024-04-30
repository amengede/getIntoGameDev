#include "frame.h"
#include "memory.h"
#include "../vkImage/image.h"

void vkUtil::SwapChainFrame::make_descriptor_resources() {

	BufferInputChunk input;
	input.logicalDevice = logicalDevice;
	input.memoryProperties = vk::MemoryPropertyFlagBits::eHostVisible | vk::MemoryPropertyFlagBits::eHostCoherent;
	input.physicalDevice = physicalDevice;
	input.size = sizeof(UBO);
	input.usage = vk::BufferUsageFlagBits::eUniformBuffer;
	cameraDataBuffer = createBuffer(input);

	cameraDataWriteLocation = logicalDevice.mapMemory(cameraDataBuffer.bufferMemory, 0, sizeof(UBO));

	input.size = 1024 * sizeof(glm::mat4);
	input.usage = vk::BufferUsageFlagBits::eStorageBuffer;
	modelBuffer = createBuffer(input);

	modelBufferWriteLocation = logicalDevice.mapMemory(modelBuffer.bufferMemory, 0, 1024 * sizeof(glm::mat4));

	modelTransforms.reserve(1024);
	for (int i = 0; i < 1024; ++i) {
		modelTransforms.push_back(glm::mat4(1.0f));
	}

	/*
	typedef struct VkDescriptorBufferInfo {
		VkBuffer        buffer;
		VkDeviceSize    offset;
		VkDeviceSize    range;
	} VkDescriptorBufferInfo;
	*/
	uniformBufferDescriptor.buffer = cameraDataBuffer.buffer;
	uniformBufferDescriptor.offset = 0;
	uniformBufferDescriptor.range = sizeof(UBO);

	modelBufferDescriptor.buffer = modelBuffer.buffer;
	modelBufferDescriptor.offset = 0;
	modelBufferDescriptor.range = 1024 * sizeof(glm::mat4);

}

void vkUtil::SwapChainFrame::make_depth_resources() {

	depthFormat = vkImage::find_supported_format(
		physicalDevice,
		{ vk::Format::eD32Sfloat, vk::Format::eD24UnormS8Uint },
		vk::ImageTiling::eOptimal,
		vk::FormatFeatureFlagBits::eDepthStencilAttachment
	);

	vkImage::ImageInputChunk imageInfo;
	imageInfo.logicalDevice = logicalDevice;
	imageInfo.physicalDevice = physicalDevice;
	imageInfo.tiling = vk::ImageTiling::eOptimal;
	imageInfo.usage = vk::ImageUsageFlagBits::eDepthStencilAttachment;
	imageInfo.memoryProperties = vk::MemoryPropertyFlagBits::eDeviceLocal;
	imageInfo.width = width;
	imageInfo.height = height;
	imageInfo.format = depthFormat;
	depthBuffer = vkImage::make_image(imageInfo);
	depthBufferMemory = vkImage::make_image_memory(imageInfo, depthBuffer);
	depthBufferView = vkImage::make_image_view(
		logicalDevice, depthBuffer, depthFormat, vk::ImageAspectFlagBits::eDepth
	);
}

void vkUtil::SwapChainFrame::write_descriptor_set() {

	vk::WriteDescriptorSet writeInfo;
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

	writeInfo.dstSet = descriptorSet;
	writeInfo.dstBinding = 0;
	writeInfo.dstArrayElement = 0; //byte offset within binding for inline uniform blocks
	writeInfo.descriptorCount = 1;
	writeInfo.descriptorType = vk::DescriptorType::eUniformBuffer;
	writeInfo.pBufferInfo = &uniformBufferDescriptor;

	logicalDevice.updateDescriptorSets(writeInfo, nullptr);

	vk::WriteDescriptorSet writeInfo2;
	writeInfo2.dstSet = descriptorSet;
	writeInfo2.dstBinding = 1;
	writeInfo2.dstArrayElement = 0; //byte offset within binding for inline uniform blocks
	writeInfo2.descriptorCount = 1;
	writeInfo2.descriptorType = vk::DescriptorType::eStorageBuffer;
	writeInfo2.pBufferInfo = &modelBufferDescriptor;

	logicalDevice.updateDescriptorSets(writeInfo2, nullptr);
}

void vkUtil::SwapChainFrame::destroy() {

	logicalDevice.destroyImageView(imageView);
	logicalDevice.destroyFramebuffer(framebuffer);
	logicalDevice.destroyFence(inFlight);
	logicalDevice.destroySemaphore(imageAvailable);
	logicalDevice.destroySemaphore(renderFinished);

	logicalDevice.unmapMemory(cameraDataBuffer.bufferMemory);
	logicalDevice.freeMemory(cameraDataBuffer.bufferMemory);
	logicalDevice.destroyBuffer(cameraDataBuffer.buffer);

	logicalDevice.unmapMemory(modelBuffer.bufferMemory);
	logicalDevice.freeMemory(modelBuffer.bufferMemory);
	logicalDevice.destroyBuffer(modelBuffer.buffer);

	logicalDevice.destroyImage(depthBuffer);
	logicalDevice.freeMemory(depthBufferMemory);
	logicalDevice.destroyImageView(depthBufferView);
}