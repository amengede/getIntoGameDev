#pragma once
#include "../config.h"

struct CubeCreateInfo {
	glm::vec3 position, eulers;
};

class Cube {
public:
	glm::vec3 position, eulers;
	Cube(CubeCreateInfo* createInfo);
	void update(float rate);
};