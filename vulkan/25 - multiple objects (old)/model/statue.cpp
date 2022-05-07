#include "statue.h"

Statue::Statue(StatueCreateInfo* statueInfo) {
	this->position = statueInfo->position;
	this->eulers = statueInfo->eulers;
}

glm::vec3 Statue::getPosition() {
	return position;
}

glm::vec3 Statue::getEulers() {
	return eulers;
}