#pragma once
#include "../config.h"
#include "shader.h"
#include "quadmesh.h"

class Engine {
public:
	Engine(int width, int height);
	~Engine();

	void createShaders();
	void getShaderLocations();
	void setOnetimeShaderData();

	void createModels();
	void render();

	unsigned int shader;
	unsigned int outerSegsLoc, innerSegsLoc, lineWidthLoc;
	int width, height;
	QuadMesh* ourQuad;
};