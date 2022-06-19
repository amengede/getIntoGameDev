#include "engine.h"

Engine::Engine(int width, int height) {

	makeShaders();
	getShaderLocations();
	setOnetimeShaderData(width, height);

	//set up framebuffer
	glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
	glEnable(GL_DEPTH_TEST);
	glEnable(GL_BLEND);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	
	createModels();
	createMaterials();
}

void Engine::makeShaders() {
	litShader = util::load_shader("shaders/vertex.txt", "shaders/fragment.txt");
	unlitShader = util::load_shader("shaders/vertex_unlit.txt", "shaders/fragment_unlit.txt");
}

void Engine::getShaderLocations() {

	glUseProgram(litShader);
	std::stringstream location;
	for (int i = 0; i < 8; i++) {
		location.str("");
		location << "lights[" << i << "].color";
		lights.colorLoc[i] = glGetUniformLocation(litShader, location.str().c_str());
		location.str("");
		location << "lights[" << i << "].position";
		lights.positionLoc[i] = glGetUniformLocation(litShader, location.str().c_str());
		location.str("");
		location << "lights[" << i << "].strength";
		lights.strengthLoc[i] = glGetUniformLocation(litShader, location.str().c_str());
	}
	cameraPosLoc = glGetUniformLocation(litShader, "cameraPosition");
	modelMatrixLocationLit = glGetUniformLocation(litShader, "model");
	viewMatrixLocationLit = glGetUniformLocation(litShader, "view");

	glUseProgram(unlitShader);
	tintLocation = glGetUniformLocation(unlitShader, "tint");
	modelMatrixLocationUnlit = glGetUniformLocation(unlitShader, "model");
	viewMatrixLocationUnlit = glGetUniformLocation(unlitShader, "view");

}

void Engine::setOnetimeShaderData(int width, int height) {

	float aspectRatio = (float)width / float(height);
	glm::mat4 projection_transform = glm::perspective(45.0f, aspectRatio, 0.1f, 10.0f);
	
	glUseProgram(litShader);
	glUniform1i(glGetUniformLocation(litShader, "basicTexture"), 0);
	glUniformMatrix4fv(
		glGetUniformLocation(litShader, "projection"),
		1, GL_FALSE, glm::value_ptr(projection_transform)
	);

	glUseProgram(unlitShader);
	glUniform1i(glGetUniformLocation(unlitShader, "basicTexture"), 0);
	glUniformMatrix4fv(
		glGetUniformLocation(unlitShader, "projection"),
		1, GL_FALSE, glm::value_ptr(projection_transform)
	);
	
}

Engine::~Engine() {

	delete woodMaterial;
	delete medkitMaterial;
	delete lightMaterial;

	delete cubeModel;
	delete medkitMesh;
	delete lightMesh;

	glDeleteProgram(litShader);
	glDeleteProgram(unlitShader);
}

void Engine::createModels() {
	MeshCreateInfo cubeInfo;
	cubeInfo.filename = "models/cube.obj";
	cubeInfo.preTransform = 0.2f * glm::mat4(1.0);
	cubeModel = new ObjMesh(&cubeInfo);
	medkitMesh = new BillboardMesh(0.3f, 0.25f);
	lightMesh = new BillboardMesh(0.2f, 0.1f);
}

void Engine::createMaterials() {
	MaterialCreateInfo materialInfo;
	materialInfo.filename = "textures/wood.jpeg";
	woodMaterial = new Material(&materialInfo);
	materialInfo.filename = "textures/medkit_albedo.png";
	medkitMaterial = new Material(&materialInfo);
	materialInfo.filename = "textures/greenlight.png";
	lightMaterial = new Material(&materialInfo);
}

void Engine::render(Scene* scene) {

	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

	//lit
	glUseProgram(litShader);
	glUniformMatrix4fv(viewMatrixLocationLit, 1, GL_FALSE,
		glm::value_ptr(scene->player->viewTransform)
	);
	glUniform3fv(cameraPosLoc, 1, glm::value_ptr(scene->player->position));

	int i{ 0 };
	for (BrightBillboard* light : scene->lights) {
		glUniform3fv(lights.colorLoc[i], 1, glm::value_ptr(light->color));
		glUniform3fv(lights.positionLoc[i], 1, glm::value_ptr(light->position));
		glUniform1f(lights.strengthLoc[i], light->strength);
		++i;
	}

	woodMaterial->use();
	glBindVertexArray(cubeModel->VAO);
	glUniformMatrix4fv(modelMatrixLocationLit, 1, GL_FALSE,
		glm::value_ptr(scene->cube->modelTransform)
	);
	glDrawArrays(GL_TRIANGLES, 0, cubeModel->vertexCount);

	medkitMaterial->use();
	glBindVertexArray(medkitMesh->VAO);
	for (Billboard* medkit : scene->medkits) {
		glUniformMatrix4fv(modelMatrixLocationLit, 1, GL_FALSE,
			glm::value_ptr(medkit->modelTransform)
		);
		glDrawArrays(GL_TRIANGLES, 0, medkitMesh->vertexCount);
	}

	//unlit
	glUseProgram(unlitShader);
	glUniformMatrix4fv(
		viewMatrixLocationUnlit, 1, GL_FALSE, 
		glm::value_ptr(scene->player->viewTransform)
	);

	lightMaterial->use();
	glBindVertexArray(lightMesh->VAO);
	for (BrightBillboard* light : scene->lights) {
		glUniform3fv(tintLocation, 1, glm::value_ptr(light->color));
		glUniformMatrix4fv(modelMatrixLocationUnlit, 1, GL_FALSE,
			glm::value_ptr(light->modelTransform)
		);
		glDrawArrays(GL_TRIANGLES, 0, lightMesh->vertexCount);
	}
}