#pragma once
#include "../config.h"
#include "obj_loader.h"

class ToonMesh {
public:
	unsigned int VBO, EBO, VAO, elementCount;
	std::vector<float> vertices;
	std::vector<uint32_t> indices;

	ToonMesh(util::MeshCreateInfo* createInfo);
	void readParsedModel(std::ifstream& file);
	void writeParsedModel(const char* filename);
	void unpackData(util::ModelData modelData);
	void constructAdjacency(util::ModelData modelData);
	~ToonMesh();
};