#pragma once
#include <glm/vec3.hpp>

class Statue {
public:
	glm::vec3 position;
	glm::vec3 eulers;

	Statue(glm::vec3 position, glm::vec3 eulers);
};