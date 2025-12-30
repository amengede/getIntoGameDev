#include "engine.h"
#include "obj_loader.h"

Engine::Engine(int width, int height) {

	this->width = width;
	this->height = height;

	createShaders();
	getShaderLocations();
	setOnetimeShaderData();

	//set up framebuffer
	glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
	glEnable(GL_DEPTH_TEST);
	glEnable(GL_BLEND);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

	createModels();
	createMaterials();
}

Engine::~Engine() {
	delete woodMaterial;
	delete starMaterial;
	delete cubeModel;
	delete girlModel;
	glDeleteProgram(shader);
	glDeleteProgram(toonShader);
	glDeleteProgram(particleShader);
}

void Engine::createShaders() {

	shader = util::load_shader("shaders/vertex.txt", "shaders/fragment.txt");
	toonShader = util::load_shader("shaders/vertex_toon.txt", "shaders/fragment_toon.txt");
	particleShader = util::load_geometry_shader("shaders/vertex_particle.txt", "shaders/geometry_particle.txt", "shaders/fragment_particle.txt");

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

}

void Engine::createModels() {
	util::MeshCreateInfo meshInfo;
	meshInfo.filename = "models/cube.obj";
	meshInfo.preTransform = 0.4f * glm::mat4(1.0);
	cubeModel = new ObjMesh(&meshInfo);

	meshInfo.filename = "models/girl.obj";
	girlModel = new ToonMesh(&meshInfo);
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
	glDrawElements(GL_TRIANGLES, girlModel->elementCount, GL_UNSIGNED_INT, 0);

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

}