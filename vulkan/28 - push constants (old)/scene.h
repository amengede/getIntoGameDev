#pragma once
#include <vector>
#include "statue.h"

class Scene {
public:
	std::vector<Statue*> statues;

	Scene();

	~Scene();
};