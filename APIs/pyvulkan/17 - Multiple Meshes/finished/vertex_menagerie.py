from config import *
import memory

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
    
    def finalize(self, logical_device, physical_device):

        self.logical_device = logical_device

        input_chunk = memory.BufferInput()
        input_chunk.logical_device = logical_device
        input_chunk.physical_device = physical_device
        input_chunk.size = self.lump.nbytes
        input_chunk.usage = VK_BUFFER_USAGE_VERTEX_BUFFER_BIT

        self.vertex_buffer = memory.create_buffer(input_chunk)

        memory_location = vkMapMemory(
            device = self.logical_device, memory = self.vertex_buffer.buffer_memory, 
            offset = 0, size = input_chunk.size, flags = 0
        )
        # (location to move to, data to move, size in bytes)
        ffi.memmove(memory_location, self.lump, input_chunk.size)
        vkUnmapMemory(device = self.logical_device, memory = self.vertex_buffer.buffer_memory)
    
    def destroy(self):

        vkDestroyBuffer(
            device = self.logical_device, buffer = self.vertex_buffer.buffer, 
            pAllocator = None
        )
        vkFreeMemory(
            device = self.logical_device, 
            memory = self.vertex_buffer.buffer_memory, pAllocator = None
        )
