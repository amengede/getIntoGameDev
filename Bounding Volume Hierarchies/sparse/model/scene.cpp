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

	buildBVH();

}

Scene::~Scene() {
	delete player;
	delete root;
}

void Scene::update(float rate) {
	player->update();
}

void Scene::movePlayer(glm::vec3 dPos) {
	player->position += dPos;
	if (player->position.x < -100.0f) {
		player->position.x = -100.0f;
	}
	if (player->position.x > 100.0f) {
		player->position.x = 100.0f;
	}
	if (player->position.y < -100.0f) {
		player->position.y = -100.0f;
	}
	if (player->position.y > 100.0f) {
		player->position.y = 100.0f;
	}
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

void Scene::buildBVH() {

	glm::vec3 minCorner = glm::vec3(-100.0f, -100.0f, -100.0f);
	glm::vec3 maxCorner = glm::vec3(100.0f, 100.0f, 100.0f);

	Box3D* box = new Box3D(minCorner, maxCorner);
	root = new Node(box);
	root->spheres.reserve(spheres.size());
	for (Sphere* sphere : spheres) {
		root->spheres.push_back(sphere);
	}

	std::queue<Node*> nodes;
	nodes.push(root);
	
	while (!nodes.empty()) {
		Node* node = nodes.front();
		nodes.pop();

		if (node->spheres.size() <= node->maxSpheres) {
			node->isInternal = false;
		}
		else {
			node->isInternal = true;
			float halfLength = (node->volume->bounds[1].x - node->volume->bounds[0].x) / 2.0f;
			float halfWidth = (node->volume->bounds[1].y - node->volume->bounds[0].y) / 2.0f;
			float halfHeight = (node->volume->bounds[1].z - node->volume->bounds[0].z) / 2.0f;

			for (int i = 0; i < 2; ++i) {
				float x = node->volume->bounds[0].x + halfLength * i;
				for (int j = 0; j < 2; ++j) {
					float y = node->volume->bounds[0].y + halfWidth * j;
					for (int k = 0; k < 2; ++k) {
						float z = node->volume->bounds[0].z + halfHeight * k;

						glm::vec3 minCorner = glm::vec3(x, y, z);
						glm::vec3 maxCorner = minCorner + glm::vec3(halfLength, halfWidth, halfHeight);
						Box3D* box = new Box3D(minCorner, maxCorner);

						Node* newNode = new Node(box);
						node->children[i + 2 * j + 4 * k] = newNode;

						for (Sphere* sphere : node->spheres) {
							if (box->overlapsWith(sphere)) {
								newNode->spheres.push_back(sphere);
							}
						}

						if (newNode->spheres.size() == 0) {
							delete newNode;
							node->children[i + 2 * j + 4 * k] = nullptr;
						}
						else {
							nodes.push(newNode);
						}
					}
				}
			}

			node->spheres.clear();
		}
	}
}