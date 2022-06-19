#include "cube.h"

Cube::Cube(CubeCreateInfo* createInfo) {
	this->position = createInfo->position;
	this->eulers = createInfo->eulers;
	modelTransform = glm::mat4(1.0f);
}

void Cube::update(float rate) {
	eulers.x += 0.001f * rate;
	if (eulers.x > 360) {
		eulers.x -= 360;
	}
	eulers.y += 0.002f * rate;
	if (eulers.y > 360) {
		eulers.y -= 360;
	}

	modelTransform = glm::mat4(1.0f);
	modelTransform = glm::translate(modelTransform, position);
	modelTransform = modelTransform * glm::eulerAngleXYZ(eulers.x, eulers.y, eulers.z);
}