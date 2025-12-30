from config import *
import memory

class VertexBufferFinalizationChunk:

    
    def __init__(self):

        self.logical_device = None
        self.physical_device = None
        self.command_buffer = None
        self.queue = None

class VertexMenagerie:

    
    def __init__(self):

        self.offset = 0
        self.offsets = {}
        self.sizes = {}
        self.lump = np.array([],dtype=np.float32)
    
    def consume(self, meshType, vertexData):

        self.lump = np.append(self.lump, vertexData)

        vertexCount = int(vertexData.size // 5)

        self.offsets[meshType] = self.offset
        self.sizes[meshType] = vertexCount
        self.offset += vertexCount
    
    def finalize(self, finalization_chunk):

        self.logical_device = finalization_chunk.logical_device

        input_chunk = memory.BufferInput()
        input_chunk.logical_device = finalization_chunk.logical_device
        input_chunk.physical_device = finalization_chunk.physical_device
        input_chunk.size = self.lump.nbytes
        input_chunk.usage = VK_BUFFER_USAGE_TRANSFER_SRC_BIT
        input_chunk.memory_properties = \
            VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT
        staging_buffer = memory.create_buffer(input_chunk)

        memory_location = vkMapMemory(
            device = self.logical_device, memory = staging_buffer.buffer_memory, 
            offset = 0, size = input_chunk.size, flags = 0
        )
        # (location to move to, data to move, size in bytes)
        ffi.memmove(memory_location, self.lump, input_chunk.size)
        vkUnmapMemory(device = self.logical_device, memory = staging_buffer.buffer_memory)

        input_chunk.usage = \
            VK_BUFFER_USAGE_TRANSFER_DST_BIT | VK_BUFFER_USAGE_VERTEX_BUFFER_BIT
        input_chunk.memory_properties = VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT
        self.vertex_buffer = memory.create_buffer(input_chunk)

        memory.copy_buffer(
            src_buffer = staging_buffer, dst_buffer = self.vertex_buffer,
            size = input_chunk.size, queue = finalization_chunk.queue,
            command_buffer = finalization_chunk.command_buffer
        )

        vkDestroyBuffer(
            device = self.logical_device, buffer = staging_buffer.buffer, 
            pAllocator = None
        )
        vkFreeMemory(
            device = self.logical_device, 
            memory = staging_buffer.buffer_memory, pAllocator = None
        )

    
    def destroy(self):

        vkDestroyBuffer(
            device = self.logical_device, buffer = self.vertex_buffer.buffer, 
            pAllocator = None
        )
        vkFreeMemory(
            device = self.logical_device, 
            memory = self.vertex_buffer.buffer_memory, pAllocator = None
        )
