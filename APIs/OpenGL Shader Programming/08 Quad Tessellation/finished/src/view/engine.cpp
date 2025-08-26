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
	filepaths.geometry = "shaders/geometry.txt";
	filepaths.tcs = "shaders/tcs.txt";
	filepaths.tes = "shaders/tes.txt";
	filepaths.fragment = "shaders/fragment.txt";
	shader = util::load_shader(filepaths);

}

void Engine::getShaderLocations() {

	glUseProgram(shader);
	outerSegsLoc = glGetUniformLocation(shader, "outerSegs");
	innerSegsLoc = glGetUniformLocation(shader, "innerSegs");
	lineWidthLoc = glGetUniformLocation(shader, "lineWidth");

}

void Engine::setOnetimeShaderData() {
}

void Engine::createModels() {

	ourQuad = new QuadMesh(1.5f, 1.5f);

}

void Engine::render() {

	glClear(GL_COLOR_BUFFER_BIT);
	glUseProgram(shader);

	glUniform1f(outerSegsLoc, 1);
	glUniform1f(innerSegsLoc, 8);
	glUniform1f(lineWidthLoc, 0.001f);
	glBindVertexArray(ourQuad->VAO);
	glDrawArrays(GL_PATCHES, 0, 4);

}