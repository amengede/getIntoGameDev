#include "storage_image.h"
#include "../vkUtil/memory.h"
#include "../../control/logging.h"
#include "../vkInit/descriptors.h"

vkImage::StorageImage::StorageImage(
	vk::PhysicalDevice physicalDevice, vk::Device logicalDevice, 
	uint32_t width, uint32_t height) {

	this->logicalDevice = logicalDevice;
	this->physicalDevice = physicalDevice;

	ImageInputChunk imageInput;
	imageInput.logicalDevice = logicalDevice;
	imageInput.physicalDevice = physicalDevice;
	imageInput.format = vk::Format::eR8G8B8A8Unorm;
	imageInput.width = width;
	imageInput.height = height;
	imageInput.arrayCount = 1;
	imageInput.tiling = vk::ImageTiling::eOptimal;
	imageInput.usage = vk::ImageUsageFlagBits::eStorage | vk::ImageUsageFlagBits::eSampled;
	imageInput.memoryProperties = vk::MemoryPropertyFlagBits::eDeviceLocal;
	image = make_image(imageInput);
	imageMemory = make_image_memory(imageInput, image);
}

vkImage::StorageImage::~StorageImage() {

	logicalDevice.freeMemory(imageMemory);
	logicalDevice.destroyImage(image);
	logicalDevice.destroyImageView(imageView);
	logicalDevice.destroySampler(sampler);
}

void vkImage::StorageImage::initialize(vk::CommandBuffer commandBuffer, vk::Queue queue) {

	ImageLayoutTransitionJob transitionJob;
	transitionJob.commandBuffer = commandBuffer;
	transitionJob.queue = queue;
	transitionJob.image = image;
	transitionJob.oldLayout = vk::ImageLayout::eUndefined;
	transitionJob.newLayout = vk::ImageLayout::eGeneral;
	transitionJob.arrayCount = 1;
	transition_image_layout(transitionJob);

	make_view();

	make_sampler();

	make_descriptors();
}

void vkImage::StorageImage::make_view() {
	imageView = make_image_view(
		logicalDevice, image, vk::Format::eR8G8B8A8Unorm, vk::ImageAspectFlagBits::eColor,
		vk::ImageViewType::e2D, 1
	);
}

void vkImage::StorageImage::make_sampler() {

	/*
	typedef struct VkSamplerCreateInfo {
		VkStructureType         sType;
		const void* pNext;
		VkSamplerCreateFlags    flags;
		VkFilter                magFilter;
		VkFilter                minFilter;
		VkSamplerMipmapMode     mipmapMode;
		VkSamplerAddressMode    addressModeU;
		VkSamplerAddressMode    addressModeV;
		VkSamplerAddressMode    addressModeW;
		float                   mipLodBias;
		VkBool32                anisotropyEnable;
		float                   maxAnisotropy;
		VkBool32                compareEnable;
		VkCompareOp             compareOp;
		float                   minLod;
		float                   maxLod;
		VkBorderColor           borderColor;
		VkBool32                unnormalizedCoordinates;
	} VkSamplerCreateInfo;
	*/
	vk::SamplerCreateInfo samplerInfo;
	samplerInfo.flags = vk::SamplerCreateFlags();
	samplerInfo.minFilter = vk::Filter::eNearest;
	samplerInfo.magFilter = vk::Filter::eLinear;
	samplerInfo.addressModeU = vk::SamplerAddressMode::eRepeat;
	samplerInfo.addressModeV = vk::SamplerAddressMode::eRepeat;
	samplerInfo.addressModeW = vk::SamplerAddressMode::eRepeat;

	samplerInfo.anisotropyEnable = false;
	samplerInfo.maxAnisotropy = 1.0f;

	samplerInfo.borderColor = vk::BorderColor::eIntOpaqueBlack;
	samplerInfo.unnormalizedCoordinates = false;
	samplerInfo.compareEnable = false;
	samplerInfo.compareOp = vk::CompareOp::eAlways;

	samplerInfo.mipmapMode = vk::SamplerMipmapMode::eLinear;
	samplerInfo.mipLodBias = 0.0f;
	samplerInfo.minLod = 0.0f;
	samplerInfo.maxLod = 0.0f;

	try {
		sampler = logicalDevice.createSampler(samplerInfo);
	}
	catch (vk::SystemError err) {
		vkLogging::Logger::get_logger()->print("Failed to make sampler.");
	}

}

void vkImage::StorageImage::make_descriptors() {

	writeDescriptor.imageLayout = vk::ImageLayout::eGeneral;
	writeDescriptor.imageView = imageView;
	writeDescriptor.sampler = nullptr;

	readDescriptor.imageLayout = vk::ImageLayout::eGeneral;
	readDescriptor.imageView = imageView;
	readDescriptor.sampler = sampler;

}