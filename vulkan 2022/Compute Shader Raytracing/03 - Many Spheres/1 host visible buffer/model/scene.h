#pragma once
#include "../config.h"
#include "sphere.h"

//Size should be 64
struct SceneDescription {
	alignas(16) glm::vec3 camera_forwards;
	alignas(16) glm::vec3 camera_right;
	alignas(16) glm::vec3 camera_up;
	alignas(16) glm::vec3 camera_position;
	alignas(4) int sphereCount;
};

class Scene {

public:
	Scene();

	std::vector<Sphere> spheres;
	SceneDescription description;
};