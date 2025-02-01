#include "vertex_menagerie.h"

VertexMenagerie::VertexMenagerie() {
	offset = 0;
}
	
void VertexMenagerie::consume(meshTypes type, std::vector<float> vertexData) {

	for (float attribute : vertexData) {
		lump.push_back(attribute);
	}
	int vertexCount = static_cast<int>(vertexData.size() / 7);

	offsets.insert(std::make_pair(type, offset));
	sizes.insert(std::make_pair(type, vertexCount));

	offset += vertexCount;
}

void VertexMenagerie::finalize(vertexBufferFinalizationChunk finalizationChunk) {

	logicalDevice = finalizationChunk.logicalDevice;

	BufferInputChunk inputChunk;
	inputChunk.logicalDevice = finalizationChunk.logicalDevice;
	inputChunk.physicalDevice = finalizationChunk.physicalDevice;
	inputChunk.size = sizeof(float) * lump.size();
	inputChunk.usage = vk::BufferUsageFlagBits::eTransferSrc;
	inputChunk.memoryProperties = vk::MemoryPropertyFlagBits::eHostVisible | vk::MemoryPropertyFlagBits::eHostCoherent;
	Buffer stagingBuffer = vkUtil::createBuffer(inputChunk);

	void* memoryLocation = logicalDevice.mapMemory(stagingBuffer.bufferMemory, 0, inputChunk.size);
	memcpy(memoryLocation, lump.data(), inputChunk.size);
	logicalDevice.unmapMemory(stagingBuffer.bufferMemory);

	inputChunk.usage = vk::BufferUsageFlagBits::eTransferDst | vk::BufferUsageFlagBits::eVertexBuffer;
	inputChunk.memoryProperties = vk::MemoryPropertyFlagBits::eDeviceLocal;
	vertexBuffer = vkUtil::createBuffer(inputChunk);

	vkUtil::copyBuffer(stagingBuffer, vertexBuffer, inputChunk.size, finalizationChunk.queue, finalizationChunk.commandBuffer);

	logicalDevice.destroyBuffer(stagingBuffer.buffer);
	logicalDevice.freeMemory(stagingBuffer.bufferMemory);
}

VertexMenagerie::~VertexMenagerie() {

	logicalDevice.destroyBuffer(vertexBuffer.buffer);
	logicalDevice.freeMemory(vertexBuffer.bufferMemory);

}