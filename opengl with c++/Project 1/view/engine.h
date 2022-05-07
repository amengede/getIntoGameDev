#pragma once
#include "../config.h"
#include "../model/scene.h"
#include "shader.h"
#include "obj_mesh.h"
#include "grid.h"

class Engine {
public:
	Engine(int width, int height);
	~Engine();

	void createPalette();
	void createModels();
	void render(Scene* scene);
	void queryUniformLocations();

	unsigned int shader;
	glm::vec3 NAVY, PURPLE, PINK, ORANGE, TEAL, RED, GREEN;
	ObjMesh* mountainMesh, * rocketMesh, * sphereMesh, * ufoBaseMesh, * ufoTopMesh;
	Grid* gridMesh;
	unsigned int colorLocation, viewLocation, modelLocation;
};