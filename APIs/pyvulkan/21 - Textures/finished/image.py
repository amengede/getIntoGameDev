from config import *
import descriptors
from PIL import Image as PIL_Img
import memory
import single_time_commands

class TextureInputChunk:

    
    def __init__(self):

        self.logicalDevice = None
        self.physicalDevice = None
        self.descriptorSetLayout = None
        self.descriptorPool = None
        self.filename: str = None
        self.commandBuffer = None
        self.queue = None

class ImageCreationChunk:


    def __init__(self):

        self.width = 0
        self.height = 0
        self.logicalDevice = None
        self.physicalDevice = None
        self.tiling = None
        self.usage = None
        self.memoryProperties = None

class ImageLayoutTransitionJob:


    def __init__(self):

        self.commandBuffer = None
        self.queue = None
        self.image = None
        self.oldLayout = None
        self.newLayout = None

class ImageCopyJob:


    def __init__(self):

        self.commandBuffer = None
        self.queue = None
        self.srcBuffer = None
        self.dstImage = None
        self.width = None
        self.height = None
    
class Texture:


    def __init__(self, input: TextureInputChunk):

        self.logicalDevice = input.logicalDevice
        self.physicalDevice = input.physicalDevice
        self.descriptorSetLayout = input.descriptorSetLayout
        self.descriptorPool = input.descriptorPool
        self.filename = input.filename
        self.commandBuffer = input.commandBuffer
        self.queue = input.queue

        self.load()

        imageInfo = ImageCreationChunk()
        imageInfo.height = self.height
        imageInfo.width = self.width
        imageInfo.logicalDevice = self.logicalDevice
        imageInfo.physicalDevice = self.physicalDevice
        imageInfo.memoryProperties = VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT
        imageInfo.tiling = VK_IMAGE_TILING_OPTIMAL
        imageInfo.usage = VK_IMAGE_USAGE_SAMPLED_BIT \
            | VK_IMAGE_USAGE_TRANSFER_DST_BIT
        self.image = make_image(imageInfo)
        self.imageMemory = make_image_memory(imageInfo, self.image)

        self.populate()

        self.make_view()

        self.make_sampler()

        self.make_descriptor_set()

    def use(self, commandBuffer, pipelineLayout):

        vkCmdBindDescriptorSets(
            commandBuffer=commandBuffer, 
            pipelineBindPoint=VK_PIPELINE_BIND_POINT_GRAPHICS,
            layout = pipelineLayout,
            firstSet = 1, descriptorSetCount = 1, 
            pDescriptorSets=[self.descriptorSet,],
            dynamicOffsetCount = 0, pDynamicOffsets=[0,]
        )

    def destroy(self):

        vkFreeMemory(self.logicalDevice, self.imageMemory, None)
        vkDestroyImage(self.logicalDevice, self.image, None)
        vkDestroyImageView(self.logicalDevice, self.imageView, None)
        vkDestroySampler(self.logicalDevice, self.sampler, None)
        
    def load(self):

        self.rawImageObject = PIL_Img.open(self.filename, mode = "r")
        self.width, self.height = self.rawImageObject.size
        self.rawImageObject = self.rawImageObject.convert("RGBA")
        self.rawImageData = bytes(self.rawImageObject.tobytes())
        self.rawImageObject.close()

    def populate(self):

        #Make a staging buffer
        bufferInfo = memory.BufferInput()
        bufferInfo.logical_device = self.logicalDevice
        bufferInfo.physical_device = self.physicalDevice
        bufferInfo.memory_properties = VK_MEMORY_PROPERTY_HOST_COHERENT_BIT \
            | VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT
        bufferInfo.usage = VK_BUFFER_USAGE_TRANSFER_SRC_BIT
        bufferInfo.size = self.width * self.height * 4

        stagingBuffer = memory.create_buffer(bufferInfo)

        #Fill it
        writeLocation = vkMapMemory(
            device = self.logicalDevice, memory = stagingBuffer.buffer_memory,
            offset = 0, size = bufferInfo.size, flags = 0 
        )
        ffi.memmove(writeLocation, self.rawImageData, bufferInfo.size)
        vkUnmapMemory(self.logicalDevice, stagingBuffer.buffer_memory)
        self.rawImageData = None

        #Transition the image from undefined to copy dest
        transitionJob = ImageLayoutTransitionJob()
        transitionJob.commandBuffer = self.commandBuffer
        transitionJob.queue = self.queue
        transitionJob.image = self.image
        transitionJob.oldLayout = VK_IMAGE_LAYOUT_UNDEFINED
        transitionJob.newLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL
        transition_image_layout(transitionJob)

        #Copy from staging buffer to image
        copyJob = ImageCopyJob()
        copyJob.commandBuffer = self.commandBuffer
        copyJob.queue = self.queue
        copyJob.srcBuffer = stagingBuffer.buffer
        copyJob.dstImage = self.image
        copyJob.width = self.width
        copyJob.height = self.height
        copy_buffer_to_image(copyJob)

        #Transition the image from copy dst to shader optimal
        transitionJob.oldLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL
        transitionJob.newLayout = VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL
        transition_image_layout(transitionJob)

        #Destroy the staging buffer
        vkDestroyBuffer(self.logicalDevice, stagingBuffer.buffer, None)
        vkFreeMemory(self.logicalDevice, stagingBuffer.buffer_memory, None)

    def make_view(self):

        self.imageView = make_image_view(
            self.logicalDevice, self.image, VK_FORMAT_R8G8B8A8_UNORM
        )

    def make_sampler(self):

        """
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
        """

        samplerInfo = VkSamplerCreateInfo(
            magFilter = VK_FILTER_LINEAR,
            minFilter = VK_FILTER_NEAREST,
            addressModeU = VK_SAMPLER_ADDRESS_MODE_REPEAT,
            addressModeV = VK_SAMPLER_ADDRESS_MODE_REPEAT,
            addressModeW = VK_SAMPLER_ADDRESS_MODE_REPEAT,
            anisotropyEnable = VK_FALSE,
            maxAnisotropy = 1.0,
            borderColor = VK_BORDER_COLOR_INT_OPAQUE_BLACK,
            unnormalizedCoordinates = VK_FALSE,
            compareEnable = VK_FALSE,
            compareOp = VK_COMPARE_OP_ALWAYS,
            mipmapMode = VK_SAMPLER_MIPMAP_MODE_LINEAR,
            mipLodBias = 0,
            minLod = 0,
            maxLod = 0
        )

        self.sampler = vkCreateSampler(self.logicalDevice, samplerInfo, None)
    
    def make_descriptor_set(self):

        self.descriptorSet = descriptors.allocate_descriptor_set(
            self.logicalDevice, self.descriptorPool, self.descriptorSetLayout
        )

        descriptor = VkDescriptorImageInfo(
            imageLayout = VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL,
            imageView = self.imageView,
            sampler = self.sampler
        )

        descriptorWrite = VkWriteDescriptorSet(
            dstSet = self.descriptorSet,
            dstBinding = 0,
            dstArrayElement = 0,
            descriptorType = VK_DESCRIPTOR_TYPE_COMBINED_IMAGE_SAMPLER,
            descriptorCount = 1,
            pImageInfo = descriptor
        )

        vkUpdateDescriptorSets(
            device = self.logicalDevice, 
            descriptorWriteCount = 1, pDescriptorWrites = descriptorWrite, 
            descriptorCopyCount = 0, pDescriptorCopies = None
        )

def make_image(info: ImageCreationChunk):

    """
    typedef struct VkImageCreateInfo {
		VkStructureType          sType;
		const void* pNext;
		VkImageCreateFlags       flags;
		VkImageType              imageType;
		VkFormat                 format;
		VkExtent3D               extent;
		uint32_t                 mipLevels;
		uint32_t                 arrayLayers;
		VkSampleCountFlagBits    samples;
		VkImageTiling            tiling;
		VkImageUsageFlags        usage;
		VkSharingMode            sharingMode;
		uint32_t                 queueFamilyIndexCount;
		const uint32_t* pQueueFamilyIndices;
		VkImageLayout            initialLayout;
	} VkImageCreateInfo;
    """

    imageInfo = VkImageCreateInfo(
        imageType = VK_IMAGE_TYPE_2D, 
        extent = VkExtent3D(info.width, info.height, 1),
        mipLevels = 1, arrayLayers = 1,
        format = VK_FORMAT_R8G8B8A8_UNORM, tiling = info.tiling,
        initialLayout = VK_IMAGE_LAYOUT_UNDEFINED,
        usage = info.usage, sharingMode = VK_SHARING_MODE_EXCLUSIVE,
        samples = VK_SAMPLE_COUNT_1_BIT
    )
    
    return vkCreateImage(
        info.logicalDevice, imageInfo, None
    )

def make_image_memory(info: ImageCreationChunk, image):

    memoryRequirements = vkGetImageMemoryRequirements(info.logicalDevice, image)
    allocInfo = VkMemoryAllocateInfo(
        allocationSize = memoryRequirements.size,
        memoryTypeIndex = memory.find_memory_type_index(
            info.physicalDevice,
            memoryRequirements.memoryTypeBits, info.memoryProperties
        )
    )

    imageMemory = vkAllocateMemory(
        info.logicalDevice, allocInfo, None
    )
    vkBindImageMemory(info.logicalDevice, image, imageMemory, 0)

    return imageMemory

def transition_image_layout(job: ImageLayoutTransitionJob):

    single_time_commands.start_job(job.commandBuffer)

    """
    typedef struct VkImageSubresourceRange {
		VkImageAspectFlags    aspectMask;
		uint32_t              baseMipLevel;
		uint32_t              levelCount;
		uint32_t              baseArrayLayer;
		uint32_t              layerCount;
	} VkImageSubresourceRange;
    """
    access = VkImageSubresourceRange(
        aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
        baseMipLevel = 0,
        levelCount = 1,
        baseArrayLayer = 0,
        layerCount = 1
    )

    if (job.oldLayout == VK_IMAGE_LAYOUT_UNDEFINED
        and job.newLayout == VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL):

        srcStage = VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT
        srcAccessMask = 0

        dstStage = VK_PIPELINE_STAGE_TRANSFER_BIT
        dstAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT
    
    else:

        srcStage = VK_PIPELINE_STAGE_TRANSFER_BIT
        srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT

        dstStage = VK_PIPELINE_STAGE_FRAGMENT_SHADER_BIT
        dstAccessMask = VK_ACCESS_SHADER_READ_BIT
    
    """
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
    """
    barrier = VkImageMemoryBarrier(
        oldLayout = job.oldLayout,
        newLayout = job.newLayout,
        srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
        dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
        image = job.image,
        subresourceRange = access,
        srcAccessMask = srcAccessMask,
        dstAccessMask = dstAccessMask
    )

    vkCmdPipelineBarrier(
        commandBuffer = job.commandBuffer,
        srcStageMask = srcStage,
        dstStageMask = dstStage,
        dependencyFlags = 0,
        memoryBarrierCount = 0, pMemoryBarriers = None,
        bufferMemoryBarrierCount = 0, pBufferMemoryBarriers = None,
        imageMemoryBarrierCount = 1, pImageMemoryBarriers = barrier
    )

    single_time_commands.end_job(job.commandBuffer, job.queue)

def copy_buffer_to_image(job: ImageCopyJob):

    single_time_commands.start_job(job.commandBuffer)

    access = VkImageSubresourceLayers(
        aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
        mipLevel = 0,
        baseArrayLayer = 0,
        layerCount = 1
    )

    imageExtent = VkExtent3D(job.width, job.height, 1)
    
    imageOffset = VkOffset3D(0,0,0)

    region = VkBufferImageCopy(
        bufferOffset = 0,
        bufferRowLength = 0,
        bufferImageHeight = 0,
        imageSubresource = access,
        imageOffset = imageOffset,
        imageExtent = imageExtent
    )

    vkCmdCopyBufferToImage(
        commandBuffer = job.commandBuffer, srcBuffer = job.srcBuffer, 
        dstImage = job.dstImage, 
        dstImageLayout = VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 
        regionCount = 1, pRegions = [region,]
    )

    single_time_commands.end_job(job.commandBuffer, job.queue)

def make_image_view(logicalDevice, image, format):

    components = VkComponentMapping(
        r = VK_COMPONENT_SWIZZLE_IDENTITY,
        g = VK_COMPONENT_SWIZZLE_IDENTITY,
        b = VK_COMPONENT_SWIZZLE_IDENTITY,
        a = VK_COMPONENT_SWIZZLE_IDENTITY
    )

    subresourceRange = VkImageSubresourceRange(
        aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
        baseMipLevel = 0, levelCount = 1,
        baseArrayLayer = 0, layerCount = 1
    )

    create_info = VkImageViewCreateInfo(
        image = image, viewType = VK_IMAGE_VIEW_TYPE_2D,
        format = format, components = components,
        subresourceRange = subresourceRange
    )

    return vkCreateImageView(
        device = logicalDevice, pCreateInfo = create_info, pAllocator = None
    )