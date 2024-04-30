#include "buffer.h"

void Buffer::create_resources(vk::Device logicalDevice) {

	writeLocation = logicalDevice.mapMemory(deviceMemory, 0, size);

	descriptor.buffer = buffer;
	descriptor.offset = 0;
	descriptor.range = size;

}

void Buffer::blit(void* data, size_t _size) {

	memcpy(writeLocation, data, _size);

}

void Buffer::destroy(vk::Device logicalDevice) {

	logicalDevice.unmapMemory(deviceMemory);
	logicalDevice.freeMemory(deviceMemory);
	logicalDevice.destroyBuffer(buffer);

}