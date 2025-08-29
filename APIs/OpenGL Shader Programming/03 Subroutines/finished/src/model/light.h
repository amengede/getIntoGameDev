#pragma once
#include <glm/glm.hpp>

struct LightCreateInfo {
	glm::vec3 position, color;
	float strength;
};

class Light {
public:
	glm::vec3 position, color;
	float strength;
	Light(LightCreateInfo* createInfo);
};
