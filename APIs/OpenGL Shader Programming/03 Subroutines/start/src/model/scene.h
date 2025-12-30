#pragma once
#include <vector>
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

	Cube* cube;
	Player* player;
	std::vector<Light*> lights;
};
