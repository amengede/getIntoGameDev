#pragma once
#include <glm/glm.hpp>

struct StatueCreateInfo {
	glm::vec3 position, eulers;
};

class Statue {
public:
	Statue(StatueCreateInfo* statueInfo);
	glm::vec3 getPosition();
	glm::vec3 getEulers();
private:
	glm::vec3 position, eulers;
};