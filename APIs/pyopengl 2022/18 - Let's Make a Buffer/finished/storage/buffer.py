from config import *

class Partition:
    """
        Describes a bindable region of a buffer.
    """

    def __init__(self, size: int, offset: int, dtype: np.dtype, target: int, binding_index: int):
        """
            Create a new partition.

            Arguments:

                size: number of bytes allocated for the region

                offset: offset of the region within its buffer, in bytes

                dtype: data type of elements in the region

                target: binding target of the region

                binding_index: bind point
        """

        self.size = size
        self.offset = offset
        instantiated = np.dtype(dtype)
        element_count = int(size / instantiated.itemsize)
        self.host_memory = np.zeros(element_count, dtype)
        self.target = target
        self.binding_index = binding_index
    
    def blit(self, data: np.ndarray):
        """
            Copy all elements from the given array into the backing memory.
        """

        self.host_memory[:] = data[:len(self.host_memory)]

class Buffer:

    def __init__(self):

        self.size = 0
        self.partitions: list[Partition] = []
        self.usage = 0
        self.device_memory = 0
    
    def add_partition(self, size: int, dtype: np.dtype, usage: int, binding_index: int) -> int:
        
        offset = self.size
        padding = (256 - (offset & 255)) & 255
        self.size += size + padding
        self.usage |= usage

        self.partitions.append(Partition(size, offset + padding, dtype, usage, binding_index))

        return len(self.partitions) - 1

    def build(self):

        self.device_memory = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.device_memory)
        glBufferStorage(GL_SHADER_STORAGE_BUFFER, self.size, 
                        None, GL_DYNAMIC_STORAGE_BIT)
    
    def blit(self, partition_index: int, data: np.ndarray) -> None:

        self.partitions[partition_index].blit(data) 

        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.device_memory)

        partition = self.partitions[partition_index]
        glBufferSubData(partition.target, partition.offset, partition.size, partition.host_memory)
    
    def readFrom(self, partition_index: int) -> None:

        partition = self.partitions[partition_index]
        glBindBufferRange(partition.target, partition.binding_index, self.device_memory, partition.offset, partition.size)
    
    def destroy(self) -> None:
        """
            Free the memory.
        """

        glDeleteBuffers(1, (self.device_memory,))