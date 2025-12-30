#pragma once
#include "../config.h"

class Curve {

public:
	Curve(std::vector<glm::vec3> controlPoints, glm::vec4 color);

	std::vector<glm::vec3> controlPoints;
	glm::vec4 color;
};