#include "cube.h"
#include <glm/gtc/matrix_transform.hpp>
#define GLM_ENABLE_EXPERIMENTAL
#include <glm/gtx/euler_angles.hpp>

Cube::Cube(CubeCreateInfo* createInfo) {
	this->position = createInfo->position;
	this->eulers = createInfo->eulers;
}

void Cube::update(float rate) {
	eulers.x += 0.001 * rate;
	if (eulers.x > 360) {
		eulers.x -= 360;
	}
	eulers.y += 0.002 * rate;
	if (eulers.y > 360) {
		eulers.y -= 360;
	}

	modelTransform = glm::mat4(1.0f);
	modelTransform = glm::translate(modelTransform, position);
	modelTransform = modelTransform * glm::eulerAngleXYZ(eulers.x, eulers.y, eulers.z);
}
