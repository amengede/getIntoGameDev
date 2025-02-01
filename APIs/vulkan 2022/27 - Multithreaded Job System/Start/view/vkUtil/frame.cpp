#include "frame.h"
#include "memory.h"
#include "../vkImage/image.h"

void vkUtil::SwapChainFrame::make_descriptor_resources() {

	BufferInputChunk input;
	input.logicalDevice = logicalDevice;
	input.memoryProperties = vk::MemoryPropertyFlagBits::eHostVisible | vk::MemoryPropertyFlagBits::eHostCoherent;
	input.physicalDevice = physicalDevice;
	input.size = sizeof(CameraVectors);
	input.usage = vk::BufferUsageFlagBits::eUniformBuffer;
	cameraVectorBuffer = createBuffer(input);

	cameraVectorWriteLocation = logicalDevice.mapMemory(cameraVectorBuffer.bufferMemory, 0, sizeof(CameraVectors));

	input.size = sizeof(CameraMatrices);
	cameraMatrixBuffer = createBuffer(input);

	cameraMatrixWriteLocation = logicalDevice.mapMemory(cameraMatrixBuffer.bufferMemory, 0, sizeof(CameraMatrices));

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
	cameraVectorDescriptor.buffer = cameraVectorBuffer.buffer;
	cameraVectorDescriptor.offset = 0;
	cameraVectorDescriptor.range = sizeof(CameraVectors);

	cameraMatrixDescriptor.buffer = cameraMatrixBuffer.buffer;
	cameraMatrixDescriptor.offset = 0;
	cameraMatrixDescriptor.range = sizeof(CameraMatrices);

	ssboDescriptor.buffer = modelBuffer.buffer;
	ssboDescriptor.offset = 0;
	ssboDescriptor.range = 1024 * sizeof(glm::mat4);

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
	imageInfo.arrayCount = 1;
	depthBuffer = vkImage::make_image(imageInfo);
	depthBufferMemory = vkImage::make_image_memory(imageInfo, depthBuffer);
	depthBufferView = vkImage::make_image_view(
		logicalDevice, depthBuffer, depthFormat, vk::ImageAspectFlagBits::eDepth,
		vk::ImageViewType::e2D, 1
	);
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
	vk::WriteDescriptorSet cameraVectorWriteOp, cameraMatrixWriteOp, ssboWriteOp;

	cameraVectorWriteOp.dstSet = descriptorSet[pipelineType::SKY];
	cameraVectorWriteOp.dstBinding = 0;
	cameraVectorWriteOp.dstArrayElement = 0; //byte offset within binding for inline uniform blocks
	cameraVectorWriteOp.descriptorCount = 1;
	cameraVectorWriteOp.descriptorType = vk::DescriptorType::eUniformBuffer;
	cameraVectorWriteOp.pBufferInfo = &cameraVectorDescriptor;

	cameraMatrixWriteOp.dstSet = descriptorSet[pipelineType::STANDARD];
	cameraMatrixWriteOp.dstBinding = 0;
	cameraMatrixWriteOp.dstArrayElement = 0; //byte offset within binding for inline uniform blocks
	cameraMatrixWriteOp.descriptorCount = 1;
	cameraMatrixWriteOp.descriptorType = vk::DescriptorType::eUniformBuffer;
	cameraMatrixWriteOp.pBufferInfo = &cameraMatrixDescriptor;

	ssboWriteOp.dstSet = descriptorSet[pipelineType::STANDARD];
	ssboWriteOp.dstBinding = 1;
	ssboWriteOp.dstArrayElement = 0; //byte offset within binding for inline uniform blocks
	ssboWriteOp.descriptorCount = 1;
	ssboWriteOp.descriptorType = vk::DescriptorType::eStorageBuffer;
	ssboWriteOp.pBufferInfo = &ssboDescriptor;

	writeOps = { cameraVectorWriteOp,cameraMatrixWriteOp,ssboWriteOp };

}

void vkUtil::SwapChainFrame::write_descriptor_set() {

	logicalDevice.updateDescriptorSets(writeOps, nullptr);
}

void vkUtil::SwapChainFrame::destroy() {

	logicalDevice.destroyImageView(imageView);
	logicalDevice.destroyFramebuffer(framebuffer[pipelineType::SKY]);
	logicalDevice.destroyFramebuffer(framebuffer[pipelineType::STANDARD]);
	logicalDevice.destroyFence(inFlight);
	logicalDevice.destroySemaphore(imageAvailable);
	logicalDevice.destroySemaphore(renderFinished);

	logicalDevice.unmapMemory(cameraVectorBuffer.bufferMemory);
	logicalDevice.freeMemory(cameraVectorBuffer.bufferMemory);
	logicalDevice.destroyBuffer(cameraVectorBuffer.buffer);

	logicalDevice.unmapMemory(cameraMatrixBuffer.bufferMemory);
	logicalDevice.freeMemory(cameraMatrixBuffer.bufferMemory);
	logicalDevice.destroyBuffer(cameraMatrixBuffer.buffer);

	logicalDevice.unmapMemory(modelBuffer.bufferMemory);
	logicalDevice.freeMemory(modelBuffer.bufferMemory);
	logicalDevice.destroyBuffer(modelBuffer.buffer);

	logicalDevice.destroyImage(depthBuffer);
	logicalDevice.freeMemory(depthBufferMemory);
	logicalDevice.destroyImageView(depthBufferView);
}