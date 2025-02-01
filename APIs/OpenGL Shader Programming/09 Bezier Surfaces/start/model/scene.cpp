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

	std::vector<glm::vec3> controlPoints = { {
		glm::vec3(0.0f,0.0f,0.5f),
		glm::vec3(-0.5f,0.5f,0.7f),
		glm::vec3(0.5f,-0.5f,0.9f),
		glm::vec3(0.0f,0.0f,1.1f),
	} };
	smoke = new Curve(controlPoints, glm::vec4(0.5, 0.25, 0.5, 1.0));

	std::vector<glm::vec3> corners = { {
		glm::vec3(-1.0f,3.0f,0.0f),
		glm::vec3(1.0f,1.0f,0.0f),
	} };
	surface = new ElasticSurface(corners, glm::vec4(0.5, 0.25, 0.5, 1.0));
}

Scene::~Scene() {
	delete cube;
	delete cube2;
	delete player;
	for (Light* light : lights) {
		delete light;
	}
	delete surface;
}

void Scene::update(float rate) {
	player->update();
	cube->update(rate);
	cube2->update(rate);

	makeParticles(glm::vec3(0, 0, 0.5), glm::normalize(glm::vec3(1, 0, 1)), glm::vec3(0, 0, -1));

	for (int i = 0; i < particles.size(); ++i) {

		Particle* particle = particles[i];
		particle->update(rate);

		if (particle->t >= particle->lifetime) {
			delete particle;
			particles.erase(particles.begin() + i--);
		}

	}

	surface->Update(rate);
}

void Scene::makeParticles(glm::vec3 position, glm::vec3 incident, glm::vec3 normal) {

	unsigned seed = std::chrono::steady_clock::now().time_since_epoch().count();
	std::default_random_engine generator(seed);

	ParticleCreateInfo createInfo;
	createInfo.acceleration = glm::vec3(0, 0, -0.001);
	createInfo.color = glm::vec3(1.0);
	createInfo.position = position;

	for (int i = 0; i < 2; ++i) {
		float x = float(generator() % 100) / 50.f - 1.0f;
		float y = float(generator() % 100) / 50.f - 1.0f;
		float z = float(generator() % 100) / 50.f - 1.0f;

		glm::vec3 randomization = glm::vec3(x, y, z);
		glm::vec3 randomizedNormal = glm::normalize(0.9f * randomization + normal);

		x = float(generator() % 100) / 10000.0f;
		glm::vec3 outgoing = x * glm::reflect(incident, randomizedNormal);

		createInfo.velocity = outgoing;

		x = 50.0f + float(generator() % 100) / 5.0f;
		createInfo.lifetime = x;

		particles.push_back(new Particle(&createInfo));
	}
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