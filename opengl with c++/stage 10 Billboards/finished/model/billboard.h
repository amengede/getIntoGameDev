#pragma once
#include "../config.h"

class Billboard {

public:

	glm::vec3 position;
	glm::mat4 modelTransform;

	Billboard(glm::vec3 position);
	void update(glm::vec3 playerPosition);
};