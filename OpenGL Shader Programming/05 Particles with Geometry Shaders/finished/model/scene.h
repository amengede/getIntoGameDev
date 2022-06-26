#pragma once
#include "../config.h"
#include "cube.h"
#include "player.h"
#include "light.h"
#include "particle.h"

class Scene {
public:
	Scene();
	~Scene();
	void update(float rate);
	void movePlayer(glm::vec3 dPos);
	void spinPlayer(glm::vec3 dEulers);
	void makeParticles(glm::vec3 position, glm::vec3 incident, glm::vec3 normal);

	Cube* cube, *cube2;
	Cube* girl;
	Player* player;
	std::vector<Light*> lights;
	std::vector<Particle*> particles;
};