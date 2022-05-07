#include "engine.h"

Engine::Engine(int width, int height) {

	shader = util::load_shader("shaders/vertex.txt", "shaders/fragment.txt");
	glUseProgram(shader);

	glUniform1i(glGetUniformLocation(shader, "basicTexture"), 0);

	float aspectRatio = (float)width / float(height);
	//set up framebuffer
	glClearColor(0.5f, 0.1f, 0.3f, 1.0f);
	glEnable(GL_DEPTH_TEST);
	glm::mat4 projection_transform = glm::perspective(45.0f, aspectRatio, 0.1f, 10.0f);
	glUniformMatrix4fv(
		glGetUniformLocation(shader, "projection"), 
		1, GL_FALSE, glm::value_ptr(projection_transform)
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
	RectangleModelCreateInfo cubeInfo;
	cubeInfo.size = { 2.0f, 1.0f, 1.0f };
	cubeModel = new RectangleModel(&cubeInfo);
}

void Engine::createMaterials() {
	MaterialCreateInfo materialInfo;
	materialInfo.filename = "textures/wood.jpeg";
	woodMaterial = new Material(&materialInfo);
}

void Engine::render(Scene* scene) {

	//prepare shaders
	glm::mat4 view_transform{
		glm::lookAt(
			scene->player->position,
			scene->player->position + scene->player->forwards,
			scene->player->up
		)
	};
	glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE,
		glm::value_ptr(view_transform));

	glm::mat4 model_transform{ glm::mat4(1.0f) };
	model_transform = glm::translate(model_transform, scene->cube->position);
	model_transform =
		model_transform * glm::eulerAngleXYZ(
			scene->cube->eulers.x, scene->cube->eulers.y, scene->cube->eulers.z
		);
	glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE,
		glm::value_ptr(model_transform));

	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
	glUseProgram(shader);
	woodMaterial->use();
	glBindVertexArray(cubeModel->VAO);
	glDrawArrays(GL_TRIANGLES, 0, cubeModel->vertexCount);
}