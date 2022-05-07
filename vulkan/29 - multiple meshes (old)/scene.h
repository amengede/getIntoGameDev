#pragma once
#include <vector>
#include "statue.h"
#include "ground.h"

class Scene {
public:
	std::vector<Statue*> statues;

	std::vector<Ground*> groundPieces;

	Scene();

	~Scene();
};