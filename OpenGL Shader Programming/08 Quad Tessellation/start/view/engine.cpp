#include "engine.h"

Engine::Engine(int width, int height) {

	this->width = width;
	this->height = height;

	createShaders();
	getShaderLocations();
	setOnetimeShaderData();

	//set up opengl stuff
	glClearColor(1.0f, 1.0f, 1.0f, 1.0f);
	glPatchParameteri(GL_PATCH_VERTICES, 4);

	createModels();
}

Engine::~Engine() {
	delete ourQuad;
	glDeleteProgram(shader);
}

void Engine::createShaders() {

	util::shaderFilePathBundle filepaths;
	filepaths.vertex = "shaders/vertex.txt";
	filepaths.geometry = NULL;
	filepaths.tcs = NULL;
	filepaths.tes = NULL;
	filepaths.fragment = "shaders/fragment.txt";
	shader = util::load_shader(filepaths);

}

void Engine::getShaderLocations() {

	glUseProgram(shader);

}

void Engine::setOnetimeShaderData() {
}

void Engine::createModels() {

	ourQuad = new QuadMesh(1.5f, 1.5f);

}

void Engine::render() {

	glClear(GL_COLOR_BUFFER_BIT);
	glUseProgram(shader);

	glBindVertexArray(ourQuad->VAO);
	glDrawArrays(GL_TRIANGLES, 0, ourQuad->vertexCount);

}