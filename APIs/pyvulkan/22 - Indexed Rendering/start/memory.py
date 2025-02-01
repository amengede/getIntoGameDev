from config import *
import single_time_commands

class BufferInput:
    """
        Holds the objects needed to create a vkBuffer
    """


    def __init__(self):

        self.size = None
        self.usage = None
        self.logical_device = None
        self.physical_device = None
        self.memory_properties = None

class Buffer:

    
    def __init__(self):

        self.buffer = None
        self.buffer_memory = None

def create_buffer(input_chunk: BufferInput) -> Buffer:
    """
        Create and return a vkBuffer
    """

    """
    typedef struct VkBufferCreateInfo {
        VkStructureType        sType;
        const void*            pNext;
        VkBufferCreateFlags    flags;
        VkDeviceSize           size;
        VkBufferUsageFlags     usage;
        VkSharingMode          sharingMode;
        uint32_t               queueFamilyIndexCount;
        const uint32_t*        pQueueFamilyIndices;
    } VkBufferCreateInfo;
    """

    bufferInfo = VkBufferCreateInfo(
        size = input_chunk.size,
        usage = input_chunk.usage,
        sharingMode = VK_SHARING_MODE_EXCLUSIVE
    )

    buffer = Buffer()
    buffer.buffer = vkCreateBuffer(
        device = input_chunk.logical_device, pCreateInfo = bufferInfo,
        pAllocator = None
    )

    allocate_buffer_memory(buffer, input_chunk)

    return buffer

def find_memory_type_index(
    physical_device, supported_memory_indices, requested_properties) -> int:

    """
    typedef struct VkPhysicalDeviceMemoryProperties {
        uint32_t        memoryTypeCount;
        VkMemoryType    memoryTypes[VK_MAX_MEMORY_TYPES];
        uint32_t        memoryHeapCount;
        VkMemoryHeap    memoryHeaps[VK_MAX_MEMORY_HEAPS];
    } VkPhysicalDeviceMemoryProperties;
    """
    memory_properties = vkGetPhysicalDeviceMemoryProperties(
        physicalDevice = physical_device
    )

    for i in range(memory_properties.memoryTypeCount):

        #bit i of supportedMemoryIndices is set if that memory type
        # is supported by the device
        supported = supported_memory_indices & (1 << i)

        #propertyFlags holds all the memory properties supported 
        # by this memory type
        sufficient = (memory_properties.memoryTypes[i].propertyFlags & requested_properties) == requested_properties

        if supported and sufficient:
            return i
    
    return 0

def allocate_buffer_memory(buffer: Buffer, input_chunk: BufferInput):

    """
    typedef struct VkMemoryRequirements {
        VkDeviceSize    size;
        VkDeviceSize    alignment;
        uint32_t        memoryTypeBits;
    } VkMemoryRequirements;
    """

    memory_requirements = vkGetBufferMemoryRequirements(
        device = input_chunk.logical_device, buffer = buffer.buffer
    )

    """
    typedef struct VkMemoryAllocateInfo {
        VkStructureType    sType;
        const void*        pNext;
        VkDeviceSize       allocationSize;
        uint32_t           memoryTypeIndex;
    } VkMemoryAllocateInfo;
    """
    allocInfo = VkMemoryAllocateInfo(
        allocationSize = memory_requirements.size,
        memoryTypeIndex = find_memory_type_index(
            physical_device = input_chunk.physical_device, 
            supported_memory_indices = memory_requirements.memoryTypeBits, 
            requested_properties = input_chunk.memory_properties
        )
    )

    buffer.buffer_memory = vkAllocateMemory(
        device = input_chunk.logical_device, pAllocateInfo = allocInfo, 
        pAllocator = None
    )

    vkBindBufferMemory(
        device = input_chunk.logical_device, buffer = buffer.buffer, 
        memory = buffer.buffer_memory, memoryOffset = 0
    )

def copy_buffer(src_buffer, dst_buffer, size, queue, command_buffer):

    single_time_commands.start_job(command_buffer)

    copyRegion = VkBufferCopy(
        srcOffset = 0, dstOffset = 0,
        size = size
    )
    vkCmdCopyBuffer(
        commandBuffer = command_buffer,
        srcBuffer = src_buffer.buffer, dstBuffer = dst_buffer.buffer,
        regionCount = 1, pRegions = [copyRegion,]
    )

    single_time_commands.end_job(command_buffer, queue)