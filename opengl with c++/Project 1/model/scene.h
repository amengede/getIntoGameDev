#pragma once
#include "../config.h"
#include "player.h"
#include "simple_component.h"
#include "enemy.h"

class Scene {
public:
	Scene();
	~Scene();
	void update(float rate);
	void movePlayer(glm::vec3 dPos);
	void shootPlayer();
	void shootEnemy(Enemy* enemy);
	void reset();

	float enemySpawnRate;
	float enemyShootRate;
	float powerUpSpawnRate;

	Player* player;
	std::vector<SimpleComponent*> bullets;
	std::vector<SimpleComponent*> powerUps;
	std::vector<Enemy*> enemies;
};