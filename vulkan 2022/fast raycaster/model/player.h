#pragma once
#include "../config.h"

class Player {
public:
	Player(float x, float y, float theta);
	void spin(float dTheta);
	glm::vec3 position, forwards, right, up;
	float theta;
};