#pragma once
#include "../config.h"
#include "obj_loader.h"

class ToonMesh {
public:
	unsigned int VBO, VAO, vertexCount;

	ToonMesh(util::MeshCreateInfo* createInfo);
	~ToonMesh();
};