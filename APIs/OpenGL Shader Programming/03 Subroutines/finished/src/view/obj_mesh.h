#pragma once
#include "../config.h"
#include "obj_loader.h"

struct MeshCreateInfo {
	const char* filename;
	glm::mat4 preTransform;
};

class ObjMesh {
public:
	unsigned int VBO, VAO, vertexCount;

	ObjMesh(MeshCreateInfo* createInfo);
	~ObjMesh();
};