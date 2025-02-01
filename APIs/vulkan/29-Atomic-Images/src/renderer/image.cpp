#include "image.h"
#include "../logging/logger.h"

StorageImage::StorageImage(VmaAllocator& allocator,
	vk::Format format,
	vk::Extent2D extent,
	vk::CommandBuffer commandBuffer,
	vk::Queue queue, vk::Device logicalDevice,
	std::deque<std::function<void(VmaAllocator)>>& vmaDeletionQueue,
	std::deque<std::function<void(vk::Device)>>& deviceDeletionQueue) {

	this->format = format;

	ImageInputChunk imageInput;
	imageInput.format = format;
	imageInput.extent = extent;
	imageInput.tiling = vk::ImageTiling::eOptimal;
	imageInput.usage = vk::ImageUsageFlagBits::eStorage | vk::ImageUsageFlagBits::eTransferSrc;
	imageInput.memoryProperties = vk::MemoryPropertyFlagBits::eDeviceLocal;
	make_image(allocator, imageInput, image, memory);

	initialize(commandBuffer, queue, logicalDevice);

	this->extent = extent;

	VkImage imageHandle = image;
	Logger* logger = Logger::get_logger();
	vmaDeletionQueue.push_back([imageHandle, logger, this](VmaAllocator allocator) {
		vmaDestroyImage(allocator, imageHandle, memory);
		logger->print("Destroyed Storage Image");
		});

	VkImageView imageViewHandle = view;
	deviceDeletionQueue.push_back([imageViewHandle, logger](vk::Device device) {
		device.destroyImageView(imageViewHandle);
		logger->print("Destroyed Storage View");
		});
}

void StorageImage::initialize(vk::CommandBuffer commandBuffer, vk::Queue queue, vk::Device logicalDevice) {

	commandBuffer.reset();
	vk::CommandBufferBeginInfo beginInfo = {};
	commandBuffer.begin(beginInfo);
	transition_image_layout(commandBuffer, image,
		vk::ImageLayout::eUndefined, vk::ImageLayout::eGeneral,
		vk::AccessFlagBits::eNoneKHR, vk::AccessFlagBits::eNoneKHR,
		vk::PipelineStageFlagBits::eNone, vk::PipelineStageFlagBits::eNone);
	commandBuffer.end();
	vk::SubmitInfo submitInfo;
	submitInfo.setCommandBufferCount(1);
	submitInfo.setPCommandBuffers(&commandBuffer);
	queue.submit(1, &submitInfo, nullptr);
	queue.waitIdle();

	make_view(logicalDevice);

	make_descriptor();
}

void StorageImage::make_view(vk::Device logicalDevice) {
	view = create_image_view(logicalDevice, image, format);
}

void StorageImage::make_descriptor() {

	descriptor.imageLayout = vk::ImageLayout::eGeneral;
	descriptor.imageView = view;
	descriptor.sampler = nullptr;
}

void make_image(VmaAllocator& allocator, ImageInputChunk input,
	vk::Image& image, VmaAllocation& memory) {

	vk::ImageCreateInfo imageInfo;
	imageInfo.flags = vk::ImageCreateFlagBits() | input.flags;
	imageInfo.imageType = vk::ImageType::e2D;
	imageInfo.extent = vk::Extent3D(input.extent, 1);
	imageInfo.mipLevels = 1;
	imageInfo.arrayLayers = 1;
	imageInfo.format = input.format;
	imageInfo.tiling = input.tiling;
	imageInfo.initialLayout = vk::ImageLayout::eUndefined;
	imageInfo.usage = input.usage;
	imageInfo.sharingMode = vk::SharingMode::eExclusive;
	imageInfo.samples = vk::SampleCountFlagBits::e1;

	VkImageCreateInfo imageCreateInfo = imageInfo;
	VkImage imageHandle;

	VmaAllocationCreateInfo allocationInfo = {};
	allocationInfo.flags = VMA_ALLOCATION_CREATE_STRATEGY_BEST_FIT_BIT;
	if (input.memoryProperties & vk::MemoryPropertyFlagBits::eHostVisible) {
		allocationInfo.flags |= VMA_ALLOCATION_CREATE_HOST_ACCESS_SEQUENTIAL_WRITE_BIT;
	}
	allocationInfo.usage = VMA_MEMORY_USAGE_AUTO;

	VmaAllocationInfo imageAllocationInfo;

	auto result = vmaCreateImage(allocator, &imageCreateInfo,
		&allocationInfo, &imageHandle, &memory,
		&imageAllocationInfo);

	Logger* logger = Logger::get_logger();

	if (result != VK_SUCCESS) {
		logger->print("Failed to create image");
		return;
	}
	logger->print("Successfully created image");

	vmaSetAllocationName(allocator, memory, "Image");
	vmaGetAllocationInfo(allocator, memory, &imageAllocationInfo);

	logger->log(imageAllocationInfo);

	image = imageHandle;
}

vk::ImageView create_image_view(
    vk::Device logicalDevice, vk::Image image, vk::Format format) {
    
    /*
    * ImageViewCreateInfo( VULKAN_HPP_NAMESPACE::ImageViewCreateFlags flags_ = {},
        VULKAN_HPP_NAMESPACE::Image                image_ = {},
        VULKAN_HPP_NAMESPACE::ImageViewType    viewType_  = VULKAN_HPP_NAMESPACE::ImageViewType::e1D,
        VULKAN_HPP_NAMESPACE::Format           format_    = VULKAN_HPP_NAMESPACE::Format::eUndefined,
        VULKAN_HPP_NAMESPACE::ComponentMapping components_            = {},
        VULKAN_HPP_NAMESPACE::ImageSubresourceRange subresourceRange_ = {} ) VULKAN_HPP_NOEXCEPT
        : flags( flags_ )
        , image( image_ )
        , viewType( viewType_ )
        , format( format_ )
        , components( components_ )
        , subresourceRange( subresourceRange_ )
    */

    vk::ImageViewCreateInfo createInfo = {};
    createInfo.image = image;
    createInfo.viewType = vk::ImageViewType::e2D;
    createInfo.format = format;
    createInfo.components.r = vk::ComponentSwizzle::eIdentity;
    createInfo.components.g = vk::ComponentSwizzle::eIdentity;
    createInfo.components.b = vk::ComponentSwizzle::eIdentity;
    createInfo.components.a = vk::ComponentSwizzle::eIdentity;
    createInfo.subresourceRange.aspectMask = vk::ImageAspectFlagBits::eColor;
    createInfo.subresourceRange.baseMipLevel = 0;
    createInfo.subresourceRange.levelCount = 1;
    createInfo.subresourceRange.baseArrayLayer = 0;
    createInfo.subresourceRange.layerCount = 1;

    return logicalDevice.createImageView(createInfo).value;
}

void transition_image_layout(vk::CommandBuffer commandBuffer, vk::Image image,
    vk::ImageLayout oldLayout, vk::ImageLayout newLayout,
	vk::AccessFlags srcAccessMask, vk::AccessFlags dstAccessMask,
	vk::PipelineStageFlags srcStage, vk::PipelineStageFlags dstStage) {

	/*
	typedef struct VkImageSubresourceRange {
		VkImageAspectFlags    aspectMask;
		uint32_t              baseMipLevel;
		uint32_t              levelCount;
		uint32_t              baseArrayLayer;
		uint32_t              layerCount;
	} VkImageSubresourceRange;
	*/
	vk::ImageSubresourceRange access;
	access.aspectMask = vk::ImageAspectFlagBits::eColor;
	access.baseMipLevel = 0;
	access.levelCount = 1;
	access.baseArrayLayer = 0;
	access.layerCount = 1;

	/*
	typedef struct VkImageMemoryBarrier {
		VkStructureType            sType;
		const void* pNext;
		VkAccessFlags              srcAccessMask;
		VkAccessFlags              dstAccessMask;
		VkImageLayout              oldLayout;
		VkImageLayout              newLayout;
		uint32_t                   srcQueueFamilyIndex;
		uint32_t                   dstQueueFamilyIndex;
		VkImage                    image;
		VkImageSubresourceRange    subresourceRange;
	} VkImageMemoryBarrier;
	*/
	vk::ImageMemoryBarrier barrier;
	barrier.oldLayout = oldLayout;
	barrier.newLayout = newLayout;
	barrier.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	barrier.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	barrier.image = image;
	barrier.subresourceRange = access;

	vk::PipelineStageFlags sourceStage, destinationStage;

	barrier.srcAccessMask = srcAccessMask;
	barrier.dstAccessMask = dstAccessMask;

	commandBuffer.pipelineBarrier(
		srcStage, dstStage, vk::DependencyFlags(), nullptr, nullptr, barrier);

}

void copy_image_to_image(vk::CommandBuffer commandBuffer,
	vk::Image src, vk::Image dst, vk::Extent2D srcSize, vk::Extent2D dstSize) {

	vk::ImageBlit2 blitRegion = {};

	// top left: 0, bottom right: 1
	blitRegion.srcOffsets[1].x = srcSize.width;
	blitRegion.srcOffsets[1].y = srcSize.height;
	blitRegion.srcOffsets[1].z = 1;

	blitRegion.dstOffsets[1].x = dstSize.width;
	blitRegion.dstOffsets[1].y = dstSize.height;
	blitRegion.dstOffsets[1].z = 1;

	blitRegion.srcSubresource.aspectMask = vk::ImageAspectFlagBits::eColor;
	blitRegion.srcSubresource.baseArrayLayer = 0;
	blitRegion.srcSubresource.layerCount = 1;
	blitRegion.srcSubresource.mipLevel = 0;

	blitRegion.dstSubresource.aspectMask = vk::ImageAspectFlagBits::eColor;
	blitRegion.dstSubresource.baseArrayLayer = 0;
	blitRegion.dstSubresource.layerCount = 1;
	blitRegion.dstSubresource.mipLevel = 0;

	vk::BlitImageInfo2 blitInfo = {};
	blitInfo.dstImage = dst;
	blitInfo.dstImageLayout = vk::ImageLayout::eTransferDstOptimal;
	blitInfo.srcImage = src;
	blitInfo.srcImageLayout = vk::ImageLayout::eTransferSrcOptimal;
	blitInfo.filter = vk::Filter::eNearest;
	blitInfo.regionCount = 1;
	blitInfo.pRegions = &blitRegion;

	commandBuffer.blitImage2(&blitInfo);
}