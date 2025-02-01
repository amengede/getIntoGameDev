#pragma once
#include "../config.h"
#include "../view/vkUtil/memory.h"

struct vertexBufferFinalizationChunk {
	vk::Device logicalDevice;
	vk::PhysicalDevice physicalDevice;
	vk::CommandBuffer commandBuffer;
	vk::Queue queue;
};

class VertexMenagerie {
public:
	VertexMenagerie();
	~VertexMenagerie();
	void consume(meshTypes type, 
		std::vector<float>& vertexData, 
		std::vector<uint32_t>& indexData);
	void finalize(vertexBufferFinalizationChunk finalizationChunk);
	Buffer vertexBuffer, indexBuffer;
	std::unordered_map<meshTypes, int> firstIndices;
	std::unordered_map<meshTypes, int> indexCounts;
private:
	int indexOffset;
	vk::Device logicalDevice;
	std::vector<float> vertexLump;
	std::vector<uint32_t> indexLump;
};