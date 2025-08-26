#pragma once
#include "../config.h"
#include "obj_loader.h"

class ObjMesh {
public:
	unsigned int VBO, EBO, VAO, elementCount;
	std::vector<float> vertices;
	std::vector<uint32_t> indices;

	ObjMesh(util::MeshCreateInfo* createInfo);
	void unpackData(util::ModelData modelData);
	~ObjMesh();
};