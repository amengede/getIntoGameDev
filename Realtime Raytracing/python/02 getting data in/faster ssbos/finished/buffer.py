from config import *
import sphere

class Buffer:

    def __init__(self, size: int, binding: int):

        self.size = size
        self.binding = binding

        # (cx cy cz r) (r g b _)
        self.hostMemory = np.zeros(8 * size, dtype=np.float32)

        self.deviceMemory = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.deviceMemory)
        glBufferStorage(
            GL_SHADER_STORAGE_BUFFER, self.hostMemory.nbytes, 
            self.hostMemory, GL_DYNAMIC_STORAGE_BIT)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, binding, self.deviceMemory)
        self.elements_written = 0
    
    def recordSphere(self, i: int, _sphere: sphere.Sphere) -> None:
        """
            Record the given sphere in position i, if this exceeds the buffer size,
            the sphere is not recorded.
        """

        if i >= self.size:
            return

        baseIndex = 8 * i
        self.hostMemory[baseIndex : baseIndex + 3] = _sphere.center[:]
        self.hostMemory[baseIndex + 3] = _sphere.radius
        self.hostMemory[baseIndex + 4 : baseIndex + 7] = _sphere.color[:]
        self.elements_written += 1
    
    def readFrom(self) -> None:
        """
            Upload the CPU data to the buffer, then arm it for reading.
        """

        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.deviceMemory)
        glBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, 8 * 4 * self.elements_written, self.hostMemory)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, self.binding, self.deviceMemory)
        self.elements_written = 0
    
    def destroy(self) -> None:
        """
            Free the memory.
        """

        glDeleteBuffers(1, (self.deviceMemory,))