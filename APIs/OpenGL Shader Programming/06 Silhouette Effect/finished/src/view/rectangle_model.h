#pragma once
#include "../config.h"

struct RectangleModelCreateInfo {
	glm::vec3 size;
};

class RectangleModel {
public:
	unsigned int VBO, VAO, vertexCount;
	std::vector<float> vertices;
	
	RectangleModel(RectangleModelCreateInfo* createInfo);
	~RectangleModel();
};