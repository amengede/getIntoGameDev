#include "scene.h"

Scene::Scene() {

	PlayerCreateInfo playerInfo;
	playerInfo.eulers = { 0.0f, 90.0f,0.0f };
	playerInfo.position = { 0.0f, 0.0f, 1.0f };
	player = new Player(&playerInfo);

	SphereCreateInfo sphereInfo;
	spheres.reserve(1000);

	for (int i = 0; i < 1000; ++i) {

		float x = random_float(-95.0f, 95.0f);
		float y = random_float(-95.0f, 95.0f);
		float z = random_float(-15.0f, 15.0f);

		float radius = random_float(0.3f, 3.0f);

		float r = random_float();
		float g = random_float();
		float b = random_float();

		sphereInfo.center = glm::vec3(x, y, z);
		sphereInfo.radius = radius;
		sphereInfo.color = glm::vec3(r, g, b);
		spheres.push_back(new Sphere(&sphereInfo));
	}

}

Scene::~Scene() {
	delete player;
}

void Scene::update(float rate) {
	player->update();
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