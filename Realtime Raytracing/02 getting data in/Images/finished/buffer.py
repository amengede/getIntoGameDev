from config import *
import sphere

class Buffer:

    def __init__(self, size: int, binding: int):

        self.size = size
        self.binding = binding

        # (cx cy cz r) (r g b _)
        self.hostMemory = np.zeros(8 * size, dtype=np.float32)

        self.deviceMemory = glGenTextures(1)
        glActiveTexture(GL_TEXTURE0 + binding)
        glBindTexture(GL_TEXTURE_2D, self.deviceMemory)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA32F,2,size,0,GL_RGBA,GL_FLOAT,bytes(self.hostMemory))
    
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
    
    def readFrom(self) -> None:
        """
            Upload the CPU data to the buffer, then arm it for reading.
        """

        glActiveTexture(GL_TEXTURE0 + self.binding)
        glBindTexture(GL_TEXTURE_2D, self.deviceMemory)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA32F,2,self.size,0,GL_RGBA,GL_FLOAT,bytes(self.hostMemory))
        glBindImageTexture(self.binding, self.deviceMemory, 0, GL_FALSE, 0, GL_READ_ONLY, GL_RGBA32F)
    
    def destroy(self) -> None:
        """
            Free the memory.
        """

        glDeleteTextures(1, (self.deviceMemory,))