#pragma once
#include "../config.h"

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