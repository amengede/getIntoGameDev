#pragma once
#include "../config.h"
#include "../view/vkUtil/memory.h"

class StarMesh {
public:
	StarMesh(vk::Device logicalDevice, vk::PhysicalDevice physicalDevice);
	~StarMesh();
	Buffer vertexBuffer;
private:
	vk::Device logicalDevice;
};