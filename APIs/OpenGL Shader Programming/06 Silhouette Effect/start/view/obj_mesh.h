#pragma once
#include "../config.h"
#include "obj_loader.h"

class ObjMesh {
public:
	unsigned int VBO, VAO, vertexCount;

	ObjMesh(util::MeshCreateInfo* createInfo);
	~ObjMesh();
};