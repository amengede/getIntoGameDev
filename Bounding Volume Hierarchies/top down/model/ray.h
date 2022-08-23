#pragma once
#include "../config.h"

class Ray {
public:
	glm::vec3 origin, direction;
	glm::vec3 invDir;
	int sign[3];

	Ray(glm::vec3 origin, glm::vec3 direction) {
		this->origin = origin;
		this->direction = direction;
		this->invDir = 1.0f / direction;
		sign[0] = (invDir.x < 0);
		sign[1] = (invDir.y < 0);
		sign[2] = (invDir.z < 0);
	}
};