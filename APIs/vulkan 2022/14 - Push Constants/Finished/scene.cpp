#include "scene.h"

Scene::Scene() {

	for (float x = -1.0f; x < 1.0f; x += 0.2f) {

		for (float y = -1.0f; y < 1.0f; y += 0.2f) {

			trianglePositions.push_back(glm::vec3(x, y, 0.0f));

		}

	}

};