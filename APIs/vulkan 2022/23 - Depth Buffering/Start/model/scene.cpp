#include "scene.h"

/**
* Scene constructor
*/
Scene::Scene() {

	float x = -0.3f;
	for (float y = -1.0f; y < 1.0f; y += 0.2f) {

		trianglePositions.push_back(glm::vec3(x, y, 0.0f));

	}

	x = 0.0f;
	for (float y = -1.0f; y < 1.0f; y += 0.2f) {

		squarePositions.push_back(glm::vec3(x, y, 0.0f));

	}

	x = 0.3f;
	for (float y = -1.0f; y < 1.0f; y += 0.2f) {

		starPositions.push_back(glm::vec3(x, y, 0.0f));

	}

};