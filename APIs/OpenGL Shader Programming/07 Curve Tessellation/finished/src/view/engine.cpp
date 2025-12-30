#include "engine.h"
#include "obj_loader.h"

Engine::Engine(int width, int height) {

	this->width = width;
	this->height = height;

	createShaders();
	getShaderLocations();
	setOnetimeShaderData();

	//set up opengl stuff
	glClearColor(1.0f, 1.0f, 1.0f, 1.0f);
	glEnable(GL_DEPTH_TEST);
	glEnable(GL_BLEND);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	glEnable(GL_CULL_FACE);
	glCullFace(GL_BACK);
	glPatchParameteri(GL_PATCH_VERTICES, 4);

	createModels();
	createMaterials();
}

Engine::~Engine() {
	delete woodMaterial;
	delete starMaterial;
	delete cubeModel;
	delete girlModel;
	delete curveMesh;
	glDeleteProgram(shader);
	glDeleteProgram(toonShader);
	glDeleteProgram(particleShader);
}

void Engine::createShaders() {

	util::shaderFilePathBundle filepaths;
	filepaths.vertex = "shaders/vertex.txt";
	filepaths.geometry = NULL;
	filepaths.tcs = NULL;
	filepaths.tes = NULL;
	filepaths.fragment = "shaders/fragment.txt";
	shader = util::load_shader(filepaths);

	filepaths.vertex = "shaders/vertex_toon.txt";
	filepaths.geometry = "shaders/geometry_toon.txt";
	filepaths.fragment = "shaders/fragment_toon.txt";
	toonShader = util::load_shader(filepaths);

	filepaths.vertex = "shaders/vertex_particle.txt";
	filepaths.geometry = "shaders/geometry_particle.txt";
	filepaths.fragment = "shaders/fragment_particle.txt";
	particleShader = util::load_shader(filepaths);

	filepaths.vertex = "shaders/curve_vertex.txt";
	filepaths.geometry = NULL;
	filepaths.tcs = "shaders/curve_tcs.txt";
	filepaths.tes = "shaders/curve_tes.txt";
	filepaths.fragment = "shaders/curve_fragment.txt";
	curveShader = util::load_shader(filepaths);

}

void Engine::getShaderLocations() {

	glUseProgram(shader);
	model.standard = glGetUniformLocation(shader, "model");
	view.standard = glGetUniformLocation(shader, "view");
	projection.standard = glGetUniformLocation(shader, "projection");
	std::stringstream location;
	for (int i = 0; i < 8; i++) {
		location.str("");
		location << "lights[" << i << "].color";
		lights.colorLoc[i] = glGetUniformLocation(shader, location.str().c_str());
		location.str("");
		location << "lights[" << i << "].position";
		lights.positionLoc[i] = glGetUniformLocation(shader, location.str().c_str());
		location.str("");
		location << "lights[" << i << "].strength";
		lights.strengthLoc[i] = glGetUniformLocation(shader, location.str().c_str());
	}
	cameraPos.standard = glGetUniformLocation(shader, "cameraPosition");
	lightingFunction.full = glGetSubroutineIndex(
		shader, GL_FRAGMENT_SHADER, "calculatePointLightFull"
	);
	lightingFunction.rough = glGetSubroutineIndex(
		shader, GL_FRAGMENT_SHADER, "calculatePointLightRough"
	);

	glUseProgram(toonShader);
	model.toon = glGetUniformLocation(toonShader, "model");
	view.toon = glGetUniformLocation(toonShader, "view");
	projection.toon = glGetUniformLocation(toonShader, "projection");
	for (int i = 0; i < 8; i++) {
		location.str("");
		location << "lights[" << i << "].color";
		toonLights.colorLoc[i] = glGetUniformLocation(toonShader, location.str().c_str());
		location.str("");
		location << "lights[" << i << "].position";
		toonLights.positionLoc[i] = glGetUniformLocation(toonShader, location.str().c_str());
		location.str("");
		location << "lights[" << i << "].strength";
		toonLights.strengthLoc[i] = glGetUniformLocation(toonShader, location.str().c_str());
	}

	glUseProgram(particleShader);
	model.particle = glGetUniformLocation(particleShader, "model");
	view.particle = glGetUniformLocation(particleShader, "view");
	projection.particle = glGetUniformLocation(particleShader, "projection");
	tint.particle = glGetUniformLocation(particleShader, "tint");

	glUseProgram(curveShader);
	model.curve = glGetUniformLocation(curveShader, "model");
	view.curve = glGetUniformLocation(curveShader, "view");
	projection.curve = glGetUniformLocation(curveShader, "projection");
	tint.curve = glGetUniformLocation(curveShader, "tint");
}

void Engine::setOnetimeShaderData() {

	float aspectRatio = (float)width / float(height);
	glm::mat4 projection_transform = glm::perspective(45.0f, aspectRatio, 0.1f, 10.0f);

	glUseProgram(shader);
	glUniform1i(glGetUniformLocation(shader, "basicTexture"), 0);
	glUniformMatrix4fv(projection.standard,
		1, GL_FALSE, glm::value_ptr(projection_transform)
	);

	glUseProgram(toonShader);
	glUniformMatrix4fv(
		projection.toon,
		1, GL_FALSE, glm::value_ptr(projection_transform)
	);

	glUseProgram(particleShader);
	glUniformMatrix4fv(
		projection.particle,
		1, GL_FALSE, glm::value_ptr(projection_transform)
	);

	glUseProgram(curveShader);
	glUniformMatrix4fv(
		projection.curve,
		1, GL_FALSE, glm::value_ptr(projection_transform)
	);
	glUniform1f(glGetUniformLocation(curveShader, "segmentCount"), 40);
	glUniform1f(glGetUniformLocation(curveShader, "stripCount"), 1);
}

void Engine::createModels() {
	util::MeshCreateInfo meshInfo;
	meshInfo.filename = "models/cube.obj";
	meshInfo.preTransform = 0.4f * glm::mat4(1.0);
	cubeModel = new ObjMesh(&meshInfo);

	meshInfo.filename = "models/girl.obj";
	meshInfo.parsed_filename = "models/girl_parsed.txt";
	girlModel = new ToonMesh(&meshInfo);

	curveMesh = new DynamicCurve();
}

void Engine::createMaterials() {
	MaterialCreateInfo materialInfo;
	materialInfo.filename = "textures/wood.jpeg";
	woodMaterial = new Material(&materialInfo);
	materialInfo.filename = "textures/star.png";
	starMaterial = new Material(&materialInfo);
}

void Engine::render(Scene* scene) {

	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

	//------- regular shader ---------//
	glUseProgram(shader);

	glUniformMatrix4fv(view.standard, 1, GL_FALSE,
		glm::value_ptr(scene->player->viewTransform)
	);

	glUniform3fv(cameraPos.standard, 1, glm::value_ptr(scene->player->position));

	int i{ 0 };
	for (Light* light : scene->lights) {
		glUniform3fv(lights.colorLoc[i], 1, glm::value_ptr(light->color));
		glUniform3fv(lights.positionLoc[i], 1, glm::value_ptr(light->position));
		glUniform1f(lights.strengthLoc[i], light->strength);
		++i;
	}

	woodMaterial->use();
	glBindVertexArray(cubeModel->VAO);
	glUniformMatrix4fv(model.standard, 1, GL_FALSE,
		glm::value_ptr(scene->cube->modelTransform)
	);
	glUniformSubroutinesuiv(GL_FRAGMENT_SHADER, 1, &lightingFunction.rough);
	glDrawElements(GL_TRIANGLES, cubeModel->elementCount, GL_UNSIGNED_INT, 0);

	glUniformMatrix4fv(model.standard, 1, GL_FALSE,
		glm::value_ptr(scene->cube2->modelTransform)
	);
	glUniformSubroutinesuiv(GL_FRAGMENT_SHADER, 1, &lightingFunction.full);
	glDrawElements(GL_TRIANGLES, cubeModel->elementCount, GL_UNSIGNED_INT, 0);

	//------- toon shader ---------//
	/*
	glUseProgram(toonShader);

	glUniformMatrix4fv(view.toon, 1, GL_FALSE,
		glm::value_ptr(scene->player->viewTransform)
	);

	i = 0;
	for (Light* light : scene->lights) {
		glUniform3fv(toonLights.colorLoc[i], 1, glm::value_ptr(light->color));
		glUniform3fv(toonLights.positionLoc[i], 1, glm::value_ptr(light->position));
		glUniform1f(toonLights.strengthLoc[i], light->strength);
		++i;
	}

	glBindVertexArray(girlModel->VAO);
	glUniformMatrix4fv(model.toon, 1, GL_FALSE,
		glm::value_ptr(scene->girl->modelTransform)
	);
	glDrawElements(GL_TRIANGLES_ADJACENCY, girlModel->elementCount, GL_UNSIGNED_INT, 0);
	*/
	//------- particle shader -----//
	glUseProgram(particleShader);

	glUniformMatrix4fv(view.particle, 1, GL_FALSE,
		glm::value_ptr(scene->player->viewTransform)
	);

	starMaterial->use();
	for (Particle* particle : scene->particles) {
		glUniformMatrix4fv(model.particle, 1, GL_FALSE,
			glm::value_ptr(particle->modelTransform)
		);
		glUniform4fv(tint.particle, 1, glm::value_ptr(particle->tint));
		glDrawArrays(GL_POINTS, 0, 1);
	}
	//------- bezier curve shader -----//
	
	glUseProgram(curveShader);

	glUniformMatrix4fv(view.curve, 1, GL_FALSE,
		glm::value_ptr(scene->player->viewTransform)
	);

	glUniformMatrix4fv(model.curve, 1, GL_FALSE,
		glm::value_ptr(glm::mat4(1.0))
	);
	glUniform4fv(tint.curve, 1, glm::value_ptr(scene->smoke->color));
	
	curveMesh->build(scene->smoke->controlPoints);
	glBindVertexArray(curveMesh->VAO);
	glDrawArrays(GL_PATCHES, 0, 4);
	
}