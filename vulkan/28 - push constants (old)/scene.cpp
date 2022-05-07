#include "scene.h"
#include <glm/vec3.hpp>

Scene::Scene() {
	statues = { {
			new Statue(
				glm::vec3(0.0f, 0.0f, 0.0f),
				glm::vec3(0.0f, 0.0f, 0.0f)
			),
		new Statue(
				glm::vec3(-1.0f, 0.0f, 0.0f),
				glm::vec3(0.0f, 0.0f, 90.0f)
			)
} };
}

Scene::~Scene() {
	for (Statue* statue : statues) {
		delete statue;
	}
	statues.clear();
}