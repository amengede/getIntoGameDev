#pragma once
#include <glm/glm.hpp>

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
