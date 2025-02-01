from config import *
import memory

class UBO:


    def __init__(self):

        self.view = pyrr.matrix44.create_identity(dtype=np.float32)
        self.projection = pyrr.matrix44.create_identity(dtype=np.float32)
        self.view_projection = pyrr.matrix44.create_identity(dtype=np.float32)

class SwapChainFrame:


    def __init__(self):
        
        #swapchain
        self.image = None
        self.image_view = None
        self.framebuffer = None

        self.commandbuffer = None

        #synchronization
        self.inFlight = None
        self.imageAvailable = None
        self.renderFinished = None

        #resources
        self.cameraData = UBO()
        self.uniformBuffer: memory.Buffer = None
        self.uniformBufferWriteLocation = None
        self.modelTransforms: np.ndarray = None
        self.modelBuffer: memory.Buffer = None
        self.modelBufferWriteLocation = None

        #resource descriptors
        self.uniformBufferDescriptor = None
        self.modelBufferDescriptor = None
        self.descriptorSet = None

    def make_descriptor_resources(self, logicalDevice, physicalDevice) -> None:

        #three matrices, each with 16 floats of 4 bytes each
        bufferSize = 3 * 16 * 4

        bufferInfo = memory.BufferInput()
        bufferInfo.logical_device = logicalDevice
        bufferInfo.physical_device = physicalDevice
        bufferInfo.memory_properties = VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT \
            | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT
        bufferInfo.size = bufferSize
        bufferInfo.usage = VK_BUFFER_USAGE_UNIFORM_BUFFER_BIT

        self.uniformBuffer = memory.create_buffer(bufferInfo)

        self.uniformBufferWriteLocation = vkMapMemory(
            device = logicalDevice, 
            memory = self.uniformBuffer.buffer_memory, 
            offset = 0, size = bufferSize, flags = 0)
        
        """
            typedef struct VkDescriptorBufferInfo {
				VkBuffer        buffer;
				VkDeviceSize    offset;
				VkDeviceSize    range;
			} VkDescriptorBufferInfo;
        """
        self.uniformBufferDescriptor = VkDescriptorBufferInfo(
            buffer = self.uniformBuffer.buffer, offset = 0, range = bufferSize
        )

        self.modelTransforms = np.array(
            [pyrr.matrix44.create_identity() for _ in range(1024)],
            dtype = np.float32
        )

        bufferSize = 1024 * 16 * 4
        bufferInfo.size = bufferSize
        bufferInfo.usage = VK_BUFFER_USAGE_STORAGE_BUFFER_BIT

        self.modelBuffer = memory.create_buffer(bufferInfo)

        self.modelBufferWriteLocation = vkMapMemory(
            device = logicalDevice, 
            memory = self.modelBuffer.buffer_memory, 
            offset = 0, size = bufferSize, flags = 0)
        
        self.modelBufferDescriptor = VkDescriptorBufferInfo(
            buffer = self.modelBuffer.buffer, offset = 0, range = bufferSize
        )
    
    def write_descriptor_set(self, device):

        """
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
        """

        descriptorWrites = [
            VkWriteDescriptorSet(
                dstSet = self.descriptorSet,
                dstBinding = 0,
                dstArrayElement = 0,
                descriptorType = VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER,
                descriptorCount = 1,
                pBufferInfo = self.uniformBufferDescriptor
            ),
            VkWriteDescriptorSet(
                dstSet = self.descriptorSet,
                dstBinding = 1,
                dstArrayElement = 0,
                descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,
                descriptorCount = 1,
                pBufferInfo = self.modelBufferDescriptor
            )
        ]
        
        vkUpdateDescriptorSets(
            device = device, 
            descriptorWriteCount = 2, 
            pDescriptorWrites = descriptorWrites, 
            descriptorCopyCount = 0, pDescriptorCopies = None
        )