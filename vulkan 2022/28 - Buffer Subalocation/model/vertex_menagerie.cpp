#include "vertex_menagerie.h"

VertexMenagerie::VertexMenagerie() {
	indexOffset = 0;
}
	
void VertexMenagerie::consume(
	meshTypes type, std::vector<float>& vertexData, 
	std::vector<uint32_t>& indexData) {

	int indexCount = static_cast<int>(indexData.size());
	int vertexCount = static_cast<int>(vertexData.size() / 11);
	int lastIndex = static_cast<int>(indexLump.size());

	firstIndices.insert(std::make_pair(type, lastIndex));
	indexCounts.insert(std::make_pair(type, indexCount));

	for (float attribute : vertexData) {
		vertexLump.push_back(attribute);
	}
	for (uint32_t index : indexData) {
		//std::cout << (index + indexOffset) << std::endl;
		indexLump.push_back(index + indexOffset);
	}

	indexOffset += vertexCount;
}

void VertexMenagerie::finalize(vertexBufferFinalizationChunk finalizationChunk) {

	vertexBufferSize = sizeof(float) * vertexLump.size();
	indexBufferSize = sizeof(uint32_t) * indexLump.size();

	logicalDevice = finalizationChunk.logicalDevice;

	//make a staging buffer for vertices
	BufferInputChunk inputChunk;
	inputChunk.logicalDevice = finalizationChunk.logicalDevice;
	inputChunk.physicalDevice = finalizationChunk.physicalDevice;
	inputChunk.size = vertexBufferSize + indexBufferSize;
	inputChunk.usage = vk::BufferUsageFlagBits::eTransferSrc;
	inputChunk.memoryProperties = vk::MemoryPropertyFlagBits::eHostVisible 
		| vk::MemoryPropertyFlagBits::eHostCoherent;
	Buffer stagingBuffer = vkUtil::createBuffer(inputChunk);

	//fill it with vertex data
	vk::DeviceSize offset = 0;
	void* memoryLocation = logicalDevice.mapMemory(stagingBuffer.bufferMemory, offset, vertexBufferSize);
	memcpy(memoryLocation, vertexLump.data(), vertexBufferSize);
	logicalDevice.unmapMemory(stagingBuffer.bufferMemory);

	//and index data
	offset = vertexBufferSize;
	memoryLocation = logicalDevice.mapMemory(stagingBuffer.bufferMemory, offset, indexBufferSize);
	memcpy(memoryLocation, indexLump.data(), indexBufferSize);
	logicalDevice.unmapMemory(stagingBuffer.bufferMemory);

	//make the buffer
	inputChunk.usage = vk::BufferUsageFlagBits::eTransferDst 
		| vk::BufferUsageFlagBits::eVertexBuffer
		| vk::BufferUsageFlagBits::eIndexBuffer;
	inputChunk.memoryProperties = vk::MemoryPropertyFlagBits::eDeviceLocal;
	buffer = vkUtil::createBuffer(inputChunk);

	//copy to it
	vkUtil::copyBuffer(
		stagingBuffer, buffer, inputChunk.size, 
		finalizationChunk.queue, finalizationChunk.commandBuffer
	);

	//destroy staging buffer
	logicalDevice.destroyBuffer(stagingBuffer.buffer);
	logicalDevice.freeMemory(stagingBuffer.bufferMemory);
	vertexLump.clear();
	indexLump.clear();
}

VertexMenagerie::~VertexMenagerie() {

	//destroy vertex buffer
	logicalDevice.destroyBuffer(buffer.buffer);
	logicalDevice.freeMemory(buffer.bufferMemory);

}