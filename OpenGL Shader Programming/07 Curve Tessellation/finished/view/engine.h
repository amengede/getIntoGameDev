#pragma once
#include "../config.h"
#include "../model/scene.h"
#include "shader.h"
#include "rectangle_model.h"
#include "obj_mesh.h"
#include "material.h"
#include "toon_mesh.h"
#include "dynamic_curve.h"

struct LightLocation {
	std::array<unsigned int, 8> colorLoc, positionLoc, strengthLoc;
};

struct ShaderLocation {
	unsigned int standard, toon, particle, curve;
};

struct LightSubroutines {
	unsigned int full, rough;
};

class Engine {
public:
	Engine(int width, int height);
	~Engine();

	void createShaders();
	void getShaderLocations();
	void setOnetimeShaderData();

	void createMaterials();
	void createModels();
	void render(Scene* scene);

	unsigned int shader, toonShader, particleShader, curveShader;
	Material* woodMaterial, * starMaterial;
	ObjMesh* cubeModel;
	ToonMesh* girlModel;
	DynamicCurve* curveMesh;
	LightLocation lights, toonLights;
	ShaderLocation cameraPos, model, view, projection, tint;
	LightSubroutines lightingFunction;
	int width, height;
};