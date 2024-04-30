#pragma once
#include "../config.h"
#include "../view/vkUtil/memory.h"

class VertexMenagerie {
public:
	VertexMenagerie();
	~VertexMenagerie();
	void consume(meshTypes type, std::vector<float> vertexData);
	void finalize(vk::Device logicalDevice, vk::PhysicalDevice physicalDevice);
	Buffer vertexBuffer;
	std::unordered_map<meshTypes, int> offsets;
	std::unordered_map<meshTypes, int> sizes;
private:
	int offset;
	vk::Device logicalDevice;
	std::vector<float> lump;
};