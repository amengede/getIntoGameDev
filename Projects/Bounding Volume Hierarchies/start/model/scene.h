#pragma once
#include "../config.h"
#include "player.h"
#include "sphere.h"

class Scene {
public:
	Scene();
	~Scene();
	void update(float rate);
	void movePlayer(glm::vec3 dPos);
	void spinPlayer(glm::vec3 dEulers);

	Player* player;
	std::vector<Sphere*> spheres;
};