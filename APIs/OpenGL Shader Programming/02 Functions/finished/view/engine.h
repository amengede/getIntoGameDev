#pragma once
#include "../config.h"
#include "shader.h"
#include "quadmesh.h"

class Engine {
public:
	Engine(int width, int height);
	~Engine();

	void create_models();

	void configure_uniform_block();

	void render();

	unsigned int shader, UBO, blockIndex;
	GLint blockSize;

	QuadMesh* ourQuad;
};