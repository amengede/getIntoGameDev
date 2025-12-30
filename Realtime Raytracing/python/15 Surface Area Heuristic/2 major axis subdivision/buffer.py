from config import *
import sphere
import node

class Buffer:

    def __init__(self, size: int, binding: int, floatCount: int, dtype: np.dtype):

        self.size = size
        self.binding = binding
        self.floatCount = floatCount

        # (cx cy cz r) (r g b _)
        self.hostMemory = np.zeros(floatCount * size, dtype=dtype)

        self.deviceMemory = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.deviceMemory)
        glBufferStorage(
            GL_SHADER_STORAGE_BUFFER, self.hostMemory.nbytes, 
            self.hostMemory, GL_DYNAMIC_STORAGE_BIT)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, binding, self.deviceMemory)
        self.elements_updated = 0
    
    def recordSphere(self, i: int, _sphere: sphere.Sphere) -> None:
        """
            Record the given sphere in position i, if this exceeds the buffer size,
            the sphere is not recorded.
        """

        if i >= self.size:
            return

        baseIndex = self.floatCount * i
        self.hostMemory[baseIndex : baseIndex + 3] = _sphere.center[:]
        self.hostMemory[baseIndex + 3] = _sphere.radius
        self.hostMemory[baseIndex + 4 : baseIndex + 7] = _sphere.color[:]
        self.hostMemory[baseIndex + 7] = _sphere.roughness

        self.elements_updated += 1
    
    def recordNode(self, i: int, _node: node.Node) -> None:
        """
            Record the given node in position i, if this exceeds the buffer size,
            the node is not recorded.
        """

        if i >= self.size:
            return

        # node: (x_min, y_min, z_min, sphere_count) (x_max, y_max, z_max, contents)
        base_index = self.floatCount * i

        self.hostMemory[base_index : base_index + 3] = _node.min_corner[:]
        self.hostMemory[base_index + 3] = _node.sphere_count

        self.hostMemory[base_index + 4 : base_index + 7] = _node.max_corner[:]
        self.hostMemory[base_index + 7]  = _node.contents

        self.elements_updated += 1
    
    def recordSphereIndex(self, i: int, index: int) -> None:
        """
            Record the given index in position i, if this exceeds the buffer size,
            the index is not recorded.
        """

        if i >= self.size:
            return
        # index: (index, _, _, _)
        base_index = self.floatCount * i

        self.hostMemory[base_index] = index

        self.elements_updated += 1
    
    def readFrom(self) -> None:
        """
            Upload the CPU data to the buffer, then arm it for reading.
        """

        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.deviceMemory)
        glBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, self.floatCount * 4 * self.elements_updated, self.hostMemory)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, self.binding, self.deviceMemory)
        self.elements_updated = 0
    
    def destroy(self) -> None:
        """
            Free the memory.
        """

        glDeleteBuffers(1, (self.deviceMemory,))