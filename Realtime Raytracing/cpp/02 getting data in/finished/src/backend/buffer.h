#pragma once
#include "../config.h"

template <typename T> class Buffer {
public:

    Buffer(size_t size, int binding): 
    size(size), binding(binding) {

        glGenBuffers(1, &deviceMemory);
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, deviceMemory);
        glBufferStorage(
            GL_SHADER_STORAGE_BUFFER, size * sizeof(T), 
            NULL, GL_DYNAMIC_STORAGE_BIT);
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, binding, deviceMemory);
    }

    ~Buffer() {
        glDeleteBuffers(1, &deviceMemory);
    }

    void blit(std::vector<T> srcData) {

        size_t srcSize = srcData.size();
        if (srcSize > size) {
            size = srcSize;
            glDeleteBuffers(1, &deviceMemory);
            glGenBuffers(1, &deviceMemory);
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, deviceMemory);
            glBufferStorage(
                GL_SHADER_STORAGE_BUFFER, size * sizeof(T), 
                srcData.data(), GL_DYNAMIC_STORAGE_BIT);
        }
        else {
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, deviceMemory);
            glBufferSubData(
                GL_SHADER_STORAGE_BUFFER, 0, size * sizeof(T), 
                srcData.data());
        }
    }

    void read_from() {
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, deviceMemory);
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, binding, deviceMemory);
    }
    
private:
    size_t size;
    int binding;
    unsigned int deviceMemory;
};