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
	void consume(meshTypes type, std::vector<float> vertexData);
	void finalize(vertexBufferFinalizationChunk finalizationChunk);
	Buffer vertexBuffer;
	std::unordered_map<meshTypes, int> offsets;
	std::unordered_map<meshTypes, int> sizes;
private:
	int offset;
	vk::Device logicalDevice;
	std::vector<float> lump;
};