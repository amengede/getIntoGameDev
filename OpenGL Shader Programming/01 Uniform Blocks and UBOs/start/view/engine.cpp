#include "engine.h"

Engine::Engine(int width, int height) {

	shader = util::load_shader("shaders/vertex.txt", "shaders/fragment.txt");
	glUseProgram(shader);

	glUniform1i(glGetUniformLocation(shader, "basicTexture"), 0);

	float aspectRatio = (float)width / float(height);
	//set up framebuffer
	glClearColor(0.0f, 0.0f, 0.0f, 1.0f);

	create_models();

}

Engine::~Engine() {
	delete ourQuad;
	glDeleteProgram(shader);
}

void Engine::create_models() {
	ourQuad = new QuadMesh(0.75f, 0.75f);
}

void Engine::render() {

	glClear(GL_COLOR_BUFFER_BIT);
	glUseProgram(shader);

	glBindVertexArray(ourQuad->VAO);
	glDrawArrays(GL_TRIANGLES, 0, ourQuad->vertexCount);

}