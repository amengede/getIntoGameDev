#include "scene.h"

Scene::Scene() {

	PlayerCreateInfo playerInfo;
	playerInfo.eulers = { 0.0f, 90.0f,0.0f };
	playerInfo.position = { 0.0f, 0.0f, 1.0f };
	player = new Player(&playerInfo);

	CubeCreateInfo cubeInfo;
	cubeInfo.eulers = { 0.0f, 0.0f, 0.0f };
	cubeInfo.position = { 3.0f, 0.0f, 0.5f };
	cube = new Cube(&cubeInfo);

	cubeInfo.position = { 3.0f, -2.0f, 0.5f };
	cube2 = new Cube(&cubeInfo);

	cubeInfo.eulers = { 90.0f, 90.0f, 0.0f };
	cubeInfo.position = { 1.0f, -2.0f, 0.5f };
	girl = new Cube(&cubeInfo);

	LightCreateInfo lightInfo;
	lightInfo.color = glm::vec3(1, 0, 0);
	lightInfo.position = glm::vec3(1, 0, 0);
	lightInfo.strength = 4.0f;
	lights.push_back(new Light(&lightInfo));
	lightInfo.color = glm::vec3(0, 1, 0);
	lightInfo.position = glm::vec3(3, 2, 0);
	lights.push_back(new Light(&lightInfo));
	lightInfo.color = glm::vec3(0, 1, 1);
	lightInfo.position = glm::vec3(3, 0, 2);
	lights.push_back(new Light(&lightInfo));
}

Scene::~Scene() {
	delete cube;
	delete cube2;
	delete player;
	for (Light* light : lights) {
		delete light;
	}
}

void Scene::update(float rate) {
	player->update();
	cube->update(rate);
	cube2->update(rate);
}

void Scene::movePlayer(glm::vec3 dPos) {
	player->position += dPos;
}

void Scene::spinPlayer(glm::vec3 dEulers) {
	player->eulers += dEulers;

	if (player->eulers.z < 0) {
		player->eulers.z += 360;
	}
	else if (player->eulers.z > 360) {
		player->eulers.z -= 360;
	}

	player->eulers.y = std::max(std::min(player->eulers.y, 179.0f), 1.0f);
}