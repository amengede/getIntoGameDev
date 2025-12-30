#pragma once
#include "../config.h"

class DynamicSurface {
public:
	unsigned int VBO, VAO, vertexCount;
	std::vector<float> vertices;

	DynamicSurface();
	void build(const std::vector<glm::vec3>& data);
	~DynamicSurface();
};