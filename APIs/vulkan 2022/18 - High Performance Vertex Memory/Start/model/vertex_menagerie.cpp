#include "vertex_menagerie.h"

VertexMenagerie::VertexMenagerie() {
	offset = 0;
}
	
void VertexMenagerie::consume(meshTypes type, std::vector<float> vertexData) {

	for (float attribute : vertexData) {
		lump.push_back(attribute);
	}
	int vertexCount = static_cast<int>(vertexData.size() / 5);

	offsets.insert(std::make_pair(type, offset));
	sizes.insert(std::make_pair(type, vertexCount));

	offset += vertexCount;
}

void VertexMenagerie::finalize(vk::Device logicalDevice, vk::PhysicalDevice physicalDevice) {

	this->logicalDevice = logicalDevice;

	BufferInputChunk inputChunk;
	inputChunk.logicalDevice = logicalDevice;
	inputChunk.physicalDevice = physicalDevice;
	inputChunk.size = sizeof(float) * lump.size();
	inputChunk.usage = vk::BufferUsageFlagBits::eVertexBuffer;

	vertexBuffer = vkUtil::createBuffer(inputChunk);

	void* memoryLocation = logicalDevice.mapMemory(vertexBuffer.bufferMemory, 0, inputChunk.size);
	memcpy(memoryLocation, lump.data(), inputChunk.size);
	logicalDevice.unmapMemory(vertexBuffer.bufferMemory);
}

VertexMenagerie::~VertexMenagerie() {

	logicalDevice.destroyBuffer(vertexBuffer.buffer);
	logicalDevice.freeMemory(vertexBuffer.bufferMemory);

}