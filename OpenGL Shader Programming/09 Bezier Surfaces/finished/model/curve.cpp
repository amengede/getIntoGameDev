#include "curve.h"

Curve::Curve(std::vector<glm::vec3> controlPoints, glm::vec4 color) {
	this->controlPoints = controlPoints;
	this->color = color;
}