#pragma once
#include "../config.h"

class QuadModel {
public:
	unsigned int VBO, VAO, vertexCount;
	std::vector<float> vertices;
	
	QuadModel();
	~QuadModel();
};