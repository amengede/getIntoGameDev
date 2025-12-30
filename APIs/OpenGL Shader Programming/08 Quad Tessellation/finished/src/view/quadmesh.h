#pragma once
#include "../config.h"

class QuadMesh {
public:
	QuadMesh(float w, float h);
	~QuadMesh();

	unsigned int VBO, VAO;
	unsigned int vertexCount;
	std::vector<float> vertices;
};