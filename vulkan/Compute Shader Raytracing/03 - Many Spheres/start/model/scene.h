#pragma once
#include "../config.h"
#include "sphere.h"

class Scene {

public:
	Scene();

	std::vector<Sphere> spheres;
};