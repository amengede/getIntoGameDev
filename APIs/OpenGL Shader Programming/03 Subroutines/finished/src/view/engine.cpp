#include "engine.h"
#include "shader.h"
#include <glad/glad.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <sstream>

Engine::Engine(int width, int height) {

	shader = util::load_shader("src/shaders/vertex.txt", "src/shaders/fragment.txt");
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

	cameraPosLoc = glGetUniformLocation(shader, "cameraPosition");

	lightingFunction.full = glGetSubroutineIndex(
		shader, GL_FRAGMENT_SHADER, "calculatePointLightFull"
	);
	lightingFunction.rough = glGetSubroutineIndex(
		shader, GL_FRAGMENT_SHADER, "calculatePointLightRough"
	);

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
	materialInfo.filename = "img/wood.jpeg";
	woodMaterial = new Material(&materialInfo);
}

void Engine::render(Scene* scene) {

	glUseProgram(shader);

	//prepare shaders
	glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE,
		glm::value_ptr(scene->player->viewTransform)
	);

	glUniform3fv(cameraPosLoc, 1, glm::value_ptr(scene->player->position));

	int i{ 0 };
	for (Light* light : scene->lights) {
		glUniform3fv(lights.colorLoc[i], 1, glm::value_ptr(light->color));
		glUniform3fv(lights.positionLoc[i], 1, glm::value_ptr(light->position));
		glUniform1f(lights.strengthLoc[i], light->strength);
		++i;
	}

	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

	woodMaterial->use();
	glBindVertexArray(cubeModel->VAO);
	glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE,
		glm::value_ptr(scene->cube->modelTransform)
	);
	glUniformSubroutinesuiv(GL_FRAGMENT_SHADER, 1, &lightingFunction.rough);
	glDrawArrays(GL_TRIANGLES, 0, cubeModel->vertexCount);

	glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE,
		glm::value_ptr(scene->cube2->modelTransform)
	);
	glUniformSubroutinesuiv(GL_FRAGMENT_SHADER, 1, &lightingFunction.full);
	glDrawArrays(GL_TRIANGLES, 0, cubeModel->vertexCount);
}
