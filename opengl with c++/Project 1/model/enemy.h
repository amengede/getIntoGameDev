#pragma once
#include "../config.h"

struct EnemyCreateInfo {
	glm::vec3 position, eulers;
};

class Enemy {
public:
	glm::vec3 position, eulers, velocity;
	STATE state;
	float health;
	bool canShoot;
	float reloadTime;
	float fallTime;
	glm::mat4 modelTransform;

	Enemy(EnemyCreateInfo* createInfo);
	void update(float rate);
};