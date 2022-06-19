#pragma once
#include "../config.h"
#include "../model/scene.h"
#include "shader.h"
#include "rectangle_model.h"
#include "obj_mesh.h"
#include "material.h"
#include "billboard_mesh.h"

struct LightLocation {
	std::array<unsigned int, 8> colorLoc, positionLoc, strengthLoc;
};

class Engine {
public:
	Engine(int width, int height);
	~Engine();

	void makeShaders();
	void getShaderLocations();
	void setOnetimeShaderData(int width, int height);
	void createMaterials();
	void createModels();
	void render(Scene* scene);

	unsigned int litShader, unlitShader;
	Material* woodMaterial, *medkitMaterial, *lightMaterial;
	ObjMesh* cubeModel;
	LightLocation lights;
	BillboardMesh* medkitMesh, *lightMesh;
	unsigned int cameraPosLoc, modelMatrixLocationLit, viewMatrixLocationLit;
	unsigned int tintLocation, modelMatrixLocationUnlit, viewMatrixLocationUnlit;
};