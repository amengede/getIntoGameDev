from config import *
import sphere
import plane

class Buffer:

    def __init__(self, size: int, binding: int, floatCount: int):

        self.size = size
        self.binding = binding
        self.floatCount = floatCount

        # (cx cy cz r) (r g b _)
        self.hostMemory = np.zeros(floatCount * size, dtype=np.float32)

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
    
    def recordPlane(self, i: int, _plane: plane.Plane) -> None:
        """
            Record the given sphere in position i, if this exceeds the buffer size,
            the sphere is not recorded.
        """

        if i >= self.size:
            return

        baseIndex = self.floatCount * i
        # plane: (cx cy cz umin) (tx ty tz umax) (bx by bz vmin) (nx ny nz vmax) (r g b -)

        self.hostMemory[baseIndex : baseIndex + 3]  = _plane.center[:]
        self.hostMemory[baseIndex + 3]              = _plane.uMin

        self.hostMemory[baseIndex + 4 : baseIndex + 7]  = _plane.tangent[:]
        self.hostMemory[baseIndex + 7]                  = _plane.uMax

        self.hostMemory[baseIndex + 8 : baseIndex + 11] = _plane.bitangent[:]
        self.hostMemory[baseIndex + 11]                 = _plane.vMin

        self.hostMemory[baseIndex + 12 : baseIndex + 15]    = _plane.normal[:]
        self.hostMemory[baseIndex + 15]                     = _plane.vMax

        self.hostMemory[baseIndex + 16] = _plane.material_index
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