#include "engine.h"

Engine::Engine(int width, int height) {

	shader = util::load_shader("shaders/vertex.txt", "shaders/fragment.txt");
	glUseProgram(shader);

	glUniform1i(glGetUniformLocation(shader, "basicTexture"), 0);

	float aspectRatio = (float)width / float(height);
	//set up framebuffer
	glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
	glEnable(GL_DEPTH_TEST);
	glm::mat4 projection_transform = glm::perspective(45.0f, aspectRatio, 0.1f, 10.0f);
	glUniformMatrix4fv(
		glGetUniformLocation(shader, "projection"), 
		1, GL_FALSE, glm::value_ptr(projection_transform)
	);
	lights.colorLoc = glGetUniformLocation(shader, "light.color");
	lights.positionLoc = glGetUniformLocation(shader, "light.position");
	lights.strengthLoc = glGetUniformLocation(shader, "light.strength");
	cameraPosLoc = glGetUniformLocation(shader, "cameraPosition");

	createModels();
	createMaterials();
}

Engine::~Engine() {
	delete woodMaterial;
	delete cubeModel;
	glDeleteProgram(shader);
}

void Engine::createModels() {
	MeshCreateInfo cubeInfo;
	cubeInfo.filename = "models/cube.obj";
	cubeInfo.preTransform = 0.2f * glm::mat4(1.0);
	cubeModel = new ObjMesh(&cubeInfo);
}

void Engine::createMaterials() {
	MaterialCreateInfo materialInfo;
	materialInfo.filename = "textures/wood.jpeg";
	woodMaterial = new Material(&materialInfo);
}

void Engine::render(Scene* scene) {

	//prepare shaders
	glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE,
		glm::value_ptr(scene->player->viewTransform)
	);

	
	glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE,
		glm::value_ptr(scene->cube->modelTransform)
	);

	glUniform3fv(cameraPosLoc, 1, glm::value_ptr(scene->player->position));

	Light* light = scene->lights[0];
	glUniform3fv(lights.colorLoc, 1, glm::value_ptr(light->color));
	glUniform3fv(lights.positionLoc, 1, glm::value_ptr(light->position));
	glUniform1f(lights.strengthLoc, light->strength);

	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
	glUseProgram(shader);
	woodMaterial->use();
	glBindVertexArray(cubeModel->VAO);
	glDrawArrays(GL_TRIANGLES, 0, cubeModel->vertexCount);
}