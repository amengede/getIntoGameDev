#pragma once
#include "../config.h"

class BillboardMesh {

public:

	std::vector<float> vertices;
	unsigned int vertexCount, VAO, VBO;

	BillboardMesh(float w, float h);
	~BillboardMesh();
};