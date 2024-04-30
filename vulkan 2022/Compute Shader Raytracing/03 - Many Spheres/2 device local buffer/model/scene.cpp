#include "scene.h"

/**
* Scene constructor
*/
Scene::Scene() {

	size_t sphereCount = 64;

	spheres.reserve(sphereCount);

	for (int i = 0; i < sphereCount; ++i) {

		float x = random_float(-10.0f, 10.0f);
		float y = random_float(-10.0f, 10.0f);
		float z = random_float(-10.0f, 10.0f);

		float radius = random_float(0.3f, 3.0f);

		float r = random_float();
		float g = random_float();
		float b = random_float();

		Sphere sphere = { glm::vec3(x, y, z), radius,  glm::vec4(r, g, b, 1.0f) };
		spheres.push_back(sphere);
	}

	description = {};
	description.sphereCount = sphereCount;
	description.camera_position = glm::vec3(0.0f);
	description.camera_forwards = glm::vec3(1.0f, 0.0f, 0.0f);
	description.camera_right = glm::vec3(0.0f, -1.0f, 0.0f);
	description.camera_up = glm::vec3(0.0f, 0.0f, 1.0f);
};