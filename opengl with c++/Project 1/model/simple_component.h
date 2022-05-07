#pragma once
#include "../config.h"

struct ComponentCreateInfo {
	glm::vec3 position, velocity;
};

class SimpleComponent {
public:
	glm::vec3 position, velocity;
	glm::mat4 modelTransform;

	SimpleComponent(ComponentCreateInfo* createInfo);
	void update(float rate);
};