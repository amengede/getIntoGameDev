#pragma once
#include "../config.h"
#include "../model/scene.h"
#include "shader.h"
#include "rectangle_model.h"
#include "obj_mesh.h"
#include "material.h"
#include "toon_mesh.h"

struct LightLocation {
	std::array<unsigned int, 8> colorLoc, positionLoc, strengthLoc;
};

struct LightSubroutines {
	unsigned int full, rough;
};

class Engine {
public:
	Engine(int width, int height);
	~Engine();

	void createMaterials();
	void createModels();
	void render(Scene* scene);

	unsigned int shader, toonShader;
	Material* woodMaterial;
	ObjMesh* cubeModel;
	ToonMesh* girlModel;
	LightLocation lights, toonLights;
	unsigned int cameraPosLoc;
	LightSubroutines lightingFunction;
};