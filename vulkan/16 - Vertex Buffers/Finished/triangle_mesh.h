#pragma once
#include "config.h"
#include "memory.h"

class TriangleMesh {
public:
	TriangleMesh(vk::Device logicalDevice, vk::PhysicalDevice physicalDevice);
	~TriangleMesh();
	Buffer vertexBuffer;
private:
	vk::Device logicalDevice;
};