#pragma once
#include "../config.h"

struct BrightbillboardCreateInfo {
	glm::vec3 position, color;
	float strength;
};

class BrightBillboard {

public:

	glm::vec3 position, color;
	glm::mat4 modelTransform;
	float strength;

	BrightBillboard(BrightbillboardCreateInfo* createInfo);
	void update(glm::vec3 playerPosition);
};