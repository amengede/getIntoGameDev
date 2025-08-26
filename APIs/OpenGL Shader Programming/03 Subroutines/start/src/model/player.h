#pragma once
#include "../config.h"

struct PlayerCreateInfo {
	glm::vec3 position, eulers;
};

class Player {
public:
	glm::vec3 position, eulers, up, forwards, right;
	glm::mat4 viewTransform;

	Player(PlayerCreateInfo* createInfo);
	void update();
};