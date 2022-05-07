#pragma once
#include "../config.h"

class Grid {
public:
	unsigned int VBO, VAO, vertexCount;

	Grid(int size);
	~Grid();
};