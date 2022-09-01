#pragma once
#include "../config.h"

class DynamicCurve {
public:
	unsigned int VBO, VAO, vertexCount;
	std::vector<float> vertices;

	DynamicCurve();
	void build(const std::vector<glm::vec3>& data);
	~DynamicCurve();
};
