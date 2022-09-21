#include "triangle_mesh.h"

TriangleMesh::TriangleMesh(vk::Device logicalDevice, vk::PhysicalDevice physicalDevice) {

	this->logicalDevice = logicalDevice;

	std::vector<float> vertices = { {
		 0.0f, -0.05f, 0.0f, 1.0f, 0.0f,
		 0.05f, 0.05f, 0.0f, 1.0f, 0.0f,
		-0.05f, 0.05f, 0.0f, 1.0f, 0.0f
	} };

	BufferInputChunk inputChunk;
	inputChunk.logicalDevice = logicalDevice;
	inputChunk.physicalDevice = physicalDevice;
	inputChunk.size = sizeof(float) * vertices.size();
	inputChunk.usage = vk::BufferUsageFlagBits::eVertexBuffer;

	vertexBuffer = vkUtil::createBuffer(inputChunk);

	void* memoryLocation = logicalDevice.mapMemory(vertexBuffer.bufferMemory, 0, inputChunk.size);
	memcpy(memoryLocation, vertices.data(), inputChunk.size);
	logicalDevice.unmapMemory(vertexBuffer.bufferMemory);
}

TriangleMesh::~TriangleMesh() {

	logicalDevice.destroyBuffer(vertexBuffer.buffer);
	logicalDevice.freeMemory(vertexBuffer.bufferMemory);

}