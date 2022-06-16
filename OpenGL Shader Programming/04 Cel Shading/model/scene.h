#pragma once
#include "../config.h"
#include "cube.h"
#include "player.h"
#include "light.h"

class Scene {
public:
	Scene();
	~Scene();
	void update(float rate);
	void movePlayer(glm::vec3 dPos);
	void spinPlayer(glm::vec3 dEulers);

	Cube* cube, *cube2;
	Cube* girl;
	Player* player;
	std::vector<Light*> lights;
};