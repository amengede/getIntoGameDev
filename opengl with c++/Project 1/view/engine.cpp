#include "engine.h"

Engine::Engine(int width, int height) {

	shader = util::load_shader("shaders/vertex.txt", "shaders/fragment.txt");
	glUseProgram(shader);

	float aspectRatio = (float)width / (float)height;
	
	glEnable(GL_DEPTH_TEST);
	glm::mat4 projection_transform = glm::perspective(45.0f, aspectRatio, 0.1f, 100.0f);
	glUniformMatrix4fv(
		glGetUniformLocation(shader, "projection"), 
		1, GL_FALSE, glm::value_ptr(projection_transform)
	);

	createModels();
	createPalette();
	queryUniformLocations();

	glClearColor(NAVY[0], NAVY[1], NAVY[2], 1.0f);
}

Engine::~Engine() {

	delete mountainMesh;
	delete gridMesh;
	delete rocketMesh;
	delete sphereMesh;
	delete ufoBaseMesh;
	delete ufoTopMesh;
	glDeleteProgram(shader);
}

void Engine::createModels() {

	MeshCreateInfo meshInfo;
	glm::mat4 preTransform = glm::mat4(1.0f);
	preTransform = glm::translate(preTransform, glm::vec3(20.0f, 0, 0.0f));
	preTransform = preTransform * glm::eulerAngleXYZ(0.0f, 0.0f, glm::radians(-90.0f));
	meshInfo.preTransform = preTransform;
	meshInfo.filename = "models/mountains.obj";
	mountainMesh = new ObjMesh(&meshInfo);


	preTransform = glm::mat4(1.0f);
	preTransform = glm::scale(preTransform, glm::vec3(0.4f, 0.4f, 0.4f));
	preTransform = preTransform * glm::eulerAngleXYZ(0.0f, 0.0f, glm::radians(90.0f));
	meshInfo.preTransform = preTransform;
	meshInfo.filename = "models/rocket.obj";
	rocketMesh = new ObjMesh(&meshInfo);

	gridMesh = new Grid(48);

	preTransform = glm::mat4(1.0f);
	preTransform = glm::scale(preTransform, glm::vec3(0.4f, 0.4f, 0.4f));
	meshInfo.preTransform = preTransform;
	meshInfo.filename = "models/basic_sphere.obj";
	sphereMesh = new ObjMesh(&meshInfo);

	preTransform = glm::mat4(1.0f);
	preTransform = glm::scale(preTransform, glm::vec3(0.2f, 0.2f, 0.2f));
	preTransform = preTransform * glm::eulerAngleXYZ(glm::radians(180.0f), 0.0f, 0.0f);
	meshInfo.preTransform = preTransform;
	meshInfo.filename = "models/ufo_base.obj";
	ufoBaseMesh = new ObjMesh(&meshInfo);

	preTransform = glm::mat4(1.0f);
	preTransform = glm::scale(preTransform, glm::vec3(0.2f, 0.2f, 0.2f));
	preTransform = preTransform * glm::eulerAngleXYZ(glm::radians(180.0f), 0.0f, 0.0f);
	meshInfo.preTransform = preTransform;
	meshInfo.filename = "models/ufo_top.obj";
	ufoTopMesh = new ObjMesh(&meshInfo);
}

void Engine::createPalette() {
	NAVY = glm::vec3(0, 13.0f / 255.0f, 107.0f / 255.0f);
	PURPLE = glm::vec3(156.0f / 255.0f, 25.0f / 255.0f, 224.0f / 255.0f);
	PINK = glm::vec3(255.0f / 255.0f, 93.0f / 255.0f, 162.0f / 255.0f);
	ORANGE = glm::vec3(255.0f / 255.0f, 162.0f / 255.0f, 93.0f / 255.0f);
	TEAL = glm::vec3(153.0f / 255.0f, 221.0f / 204.0f, 107.0f / 255.0f);
	RED = glm::vec3(255.0f / 255.0f, 93.0f / 255.0f, 93.0f / 255.0f);
	GREEN = glm::vec3(93.0f / 255.0f, 255.0f / 255.0f, 93.0f / 255.0f);
}

void Engine::queryUniformLocations() {
	colorLocation = glGetUniformLocation(shader, "color");
	modelLocation = glGetUniformLocation(shader, "model");
	viewLocation = glGetUniformLocation(shader, "view");
}

void Engine::render(Scene* scene) {
	glUseProgram(shader);
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

	glm::mat4 viewTransform = glm::lookAt(glm::vec3(-10, 0, 4), glm::vec3(0, 0, 4), glm::vec3(0, 0, 1));
	glUniformMatrix4fv(viewLocation, 1, GL_FALSE, glm::value_ptr(viewTransform));

	//mountains
	glUniform3fv(colorLocation, 1, glm::value_ptr(TEAL));
	glm::mat4 modelTransform = glm::mat4(1.0f);
	glUniformMatrix4fv(modelLocation, 1, GL_FALSE, glm::value_ptr(modelTransform));
	glBindVertexArray(mountainMesh->VAO);
	glDrawArrays(GL_LINES, 0, mountainMesh->vertexCount);

	//grid
	glUniform3fv(colorLocation, 1, glm::value_ptr(TEAL));
	modelTransform = glm::mat4(1.0f);
	modelTransform = glm::translate(modelTransform, glm::vec3(-16, -24, 0));
	glUniformMatrix4fv(modelLocation, 1, GL_FALSE, glm::value_ptr(modelTransform));
	glBindVertexArray(gridMesh->VAO);
	glDrawArrays(GL_LINES, 0, gridMesh->vertexCount);

	//player
	glUniform3fv(colorLocation, 1, glm::value_ptr(ORANGE));
	modelTransform = glm::mat4(1.0f);
	glUniformMatrix4fv(modelLocation, 1, GL_FALSE, glm::value_ptr(scene->player->modelTransform));
	glBindVertexArray(rocketMesh->VAO);
	glDrawArrays(GL_TRIANGLES, 0, rocketMesh->vertexCount);

	//bullets
	glUniform3fv(colorLocation, 1, glm::value_ptr(RED));
	for (SimpleComponent* bullet : scene->bullets) {
		modelTransform = glm::mat4(1.0f);
		glUniformMatrix4fv(modelLocation, 1, GL_FALSE, glm::value_ptr(bullet->modelTransform));
		glBindVertexArray(sphereMesh->VAO);
		glDrawArrays(GL_TRIANGLES, 0, sphereMesh->vertexCount);
	}

	//enemies
	for (Enemy* enemy : scene->enemies) {
		modelTransform = glm::mat4(1.0f);
		glUniformMatrix4fv(modelLocation, 1, GL_FALSE, glm::value_ptr(enemy->modelTransform));
		glUniform3fv(colorLocation, 1, glm::value_ptr(PURPLE));
		glBindVertexArray(ufoBaseMesh->VAO);
		glDrawArrays(GL_TRIANGLES, 0, ufoBaseMesh->vertexCount);
		glUniform3fv(colorLocation, 1, glm::value_ptr(PINK));
		glBindVertexArray(ufoTopMesh->VAO);
		glDrawArrays(GL_TRIANGLES, 0, ufoTopMesh->vertexCount);
	}

	//powerUps
	glUniform3fv(colorLocation, 1, glm::value_ptr(GREEN));
	for (SimpleComponent* powerUp : scene->powerUps) {
		modelTransform = glm::mat4(1.0f);
		glUniformMatrix4fv(modelLocation, 1, GL_FALSE, glm::value_ptr(powerUp->modelTransform));
		glBindVertexArray(sphereMesh->VAO);
		glDrawArrays(GL_TRIANGLES, 0, sphereMesh->vertexCount);
	}
}