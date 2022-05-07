#pragma once
#include "../config.h"

struct PlayerCreateInfo {
	glm::vec3 position, eulers;
};

class Player {
public:
	glm::vec3 position, eulers, velocity;
	STATE state;
	float health;
	bool canShoot;
	float reloadTime;
	float fallTime;
	glm::mat4 modelTransform;

	Player(PlayerCreateInfo* createInfo);
	void update(float rate);
};