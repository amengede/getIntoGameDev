#pragma once
#include "../config.h"
#include "cube.h"
#include "player.h"
#include "light.h"
#include "billboard.h"
#include "bright_billboard.h"

class Scene {
public:
	Scene();
	~Scene();
	void update(float rate);
	void movePlayer(glm::vec3 dPos);
	void spinPlayer(glm::vec3 dEulers);

	Cube* cube;
	Player* player;
	std::vector<BrightBillboard*> lights;
	std::vector<Billboard*> medkits;
};