#pragma once
#include "../config.h"
#include "player.h"
#include "wall.h"

struct SceneDescription {
	alignas(8) glm::vec2 forwards;
	alignas(8) glm::vec2 right;
	alignas(8) glm::vec2 position;
	alignas(4) int wallCount;
};

class Scene {
public:

	Scene();
	void update();

	Player player = Player(10.5, 27.5, 0);
	std::vector<Wall> walls;
	SceneDescription description;

private:
	void build_raycasting_environment();
};