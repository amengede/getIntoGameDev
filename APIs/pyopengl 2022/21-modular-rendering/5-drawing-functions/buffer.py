from config import *


class Partition:
    """
        Describes a bindable region of a buffer.
    """

    def __init__(self, size: int, offset: int, 
                 dtype: np.dtype, target: int, binding_index: int):
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

    def blit(self, data: np.ndarray) -> None:
        """
            Copy all elements from the given array into the backing memory.

            Parameters:

                data: numpy array of data to copy in
        """

        self.host_memory[:] = data[:len(self.host_memory)]

class Buffer:
    """
        An allocation of memory on the GPU. Regions can be bound as independent resources.

        Most commonly, buffer can either be a collection of Storage Buffers, 
        or a VBO and EBO lumped together.
    """

    def __init__(self):
        """
            Create a new buffer, with no allocation or partitions.
        """

        self.size = 0
        self.partitions: list[Partition] = []
        self.usage = 0
        self.device_memory = 0
 
    def add_partition(self, size: int,
                      dtype: np.dtype, usage: int,
                      binding_index: int = 0) -> int:
        """
            Describe a resource to be allocated on the buffer.

            Parameters:

                size: size of the resource (in bytes)

                dtype: Data type of the resource

                usage: Intended usage/target of the resource

                binding_index: For bind point resources like storage buffers,
                    intended bind point. Can be ignored for eg. VBOs

            Returns:

                The index of this partition within the buffer's set of partitions.
        """

        offset = self.size
        padding = (256 - (offset & 255)) & 255
        self.size += size + padding
        self.usage |= usage

        self.partitions.append(Partition(size, offset + padding,
                                         dtype, usage, binding_index))

        return len(self.partitions) - 1

    def build(self) -> None:
        """
            Use the Buffer's set of partitions to allocate memory on the GPU.
            This method must be called before the buffer is used.
        """

        self.device_memory = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.device_memory)
        glBufferStorage(GL_SHADER_STORAGE_BUFFER, self.size,
                        None, GL_DYNAMIC_STORAGE_BIT)

    def blit(self, partition_index: int, data: np.ndarray) -> None:
        """
            Upload data to a partition of the buffer.

            Parameters:

                partition_index: index of the partition to upload to

                data: array of data to upload
        """

        partition = self.partitions[partition_index]
        partition.blit(data)

        glBindBuffer(partition.target, self.device_memory)
        glBufferSubData(partition.target, partition.offset,
                        partition.size, partition.host_memory)

    def read_from(self, partition_index: int) -> None:
        """
            Bind a partition of the buffer for GPU usage.
            This method is intended for use with bindpoint resources.

            Parameters:

                partition_index: index of the partition to bind.
        """

        partition = self.partitions[partition_index]
        glBindBufferRange(partition.target, partition.binding_index,
                          self.device_memory, partition.offset, partition.size)

    def bind(self, partition_index: int) -> None:
        """
            Bind a partition of the buffer for GPU usage.
            This method is intended for VBO/EBO resouces.

            Parameters:

                partition_index: index of the partition to bind.
        """

        partition = self.partitions[partition_index]
        glBindBuffer(partition.target, self.device_memory)

    def destroy(self) -> None:
        """
            Free the memory.
        """

        glDeleteBuffers(1, (self.device_memory,))
