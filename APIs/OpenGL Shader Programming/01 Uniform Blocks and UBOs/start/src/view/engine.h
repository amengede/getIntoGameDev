#pragma once
#include "shader.h"
#include "quadmesh.h"

class Engine {
public:
	Engine(int width, int height);
	~Engine();

	void create_models();

	void render();

	unsigned int shader;
	QuadMesh* ourQuad;
};
