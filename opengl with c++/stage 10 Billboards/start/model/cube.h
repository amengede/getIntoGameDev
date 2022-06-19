#pragma once
#include "../config.h"

struct CubeCreateInfo {
	glm::vec3 position, eulers;
};

class Cube {
public:
	glm::vec3 position, eulers;
	glm::mat4 modelTransform;
	Cube(CubeCreateInfo* createInfo);
	void update(float rate);
};