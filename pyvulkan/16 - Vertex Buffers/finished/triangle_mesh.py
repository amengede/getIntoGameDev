from config import *
import memory

class TriangleMesh:


    def __init__(self, logical_device, physical_device):

        self.logical_device = logical_device

        vertices = np.array(
            (0.0, -0.05, 0.0, 1.0, 0.0,
             0.05, 0.05, 0.0, 1.0, 0.0,
            -0.05, 0.05, 0.0, 1.0, 0.0), dtype = np.float32
        )

        input_chunk = memory.BufferInput()
        input_chunk.logical_device = logical_device
        input_chunk.physical_device = physical_device
        input_chunk.size = vertices.nbytes
        input_chunk.usage = VK_BUFFER_USAGE_VERTEX_BUFFER_BIT

        self.vertex_buffer = memory.create_buffer(input_chunk)

        memory_location = vkMapMemory(
            device = self.logical_device, memory = self.vertex_buffer.buffer_memory, 
            offset = 0, size = input_chunk.size, flags = 0
        )
        # (location to move to, data to move, size in bytes)
        ffi.memmove(memory_location, vertices, input_chunk.size)
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