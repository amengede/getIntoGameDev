#include <cstring>
#include "engine.h"
#include "shader.h"
#include <iostream>

Engine::Engine(int width, int height) {

	shader = util::load_shader("src/shaders/vertex.txt", "src/shaders/fragment.txt");
	glUseProgram(shader);

	glUniform1i(glGetUniformLocation(shader, "basicTexture"), 0);

	float aspectRatio = (float)width / float(height);
	//set up framebuffer
	glClearColor(0.0f, 0.0f, 0.0f, 1.0f);

	create_models();

	configure_uniform_block();

}

Engine::~Engine() {
	delete ourQuad;
	glDeleteProgram(shader);
}

void Engine::create_models() {
	ourQuad = new QuadMesh(0.75f, 0.75f);
}

void Engine::configure_uniform_block() {

	blockIndex = glGetUniformBlockIndex(shader, "diskParameters");

	std::cout << "diskParameters is a uniform block occupying block index: " << blockIndex << '\n';

	glGetActiveUniformBlockiv(shader, blockIndex, GL_UNIFORM_BLOCK_DATA_SIZE, &blockSize);

	std::cout << "\ttaking up " << blockSize << " bytes\n";

	GLubyte* blockBuffer = (GLubyte*)malloc(blockSize);

	const GLchar* names[] = { "InnerColor","OuterColor", "InnerRadius", "OuterRadius"};

	GLuint indices[4];
	glGetUniformIndices(shader, 4, names, indices);

	for (int i = 0; i < 4; ++i) {
		std::cout << "attribute \"" << names[i] << "\" has index: " << indices[i] << " in the block.\n";
	}

	GLint offset[4];
	glGetActiveUniformsiv(shader, 4, indices, GL_UNIFORM_OFFSET, offset);

	for (int i = 0; i < 4; ++i) {
		std::cout << "attribute \"" << names[i] << "\" has offset: " << offset[i] << " in the block.\n";
	}

	std::vector<float> outerColor = { 0.0f, 1.0f, 0.0f, 1.0f };
	std::vector<float> innerColor = { 1.0f, 0.0f, 0.0f, 1.0f };
	float innerRadius = 0.25f;
	float outerRadius = 0.5f;

	memcpy(blockBuffer + offset[0], innerColor.data(), 4 * sizeof(float));
	memcpy(blockBuffer + offset[1], outerColor.data(), 4 * sizeof(float));
	memcpy(blockBuffer + offset[2], &innerRadius, sizeof(float));
	memcpy(blockBuffer + offset[3], &outerRadius, sizeof(float));

	glGenBuffers(1, &UBO);
	glBindBuffer(GL_UNIFORM_BUFFER, UBO);
	glBufferData(GL_UNIFORM_BUFFER, blockSize, blockBuffer, GL_DYNAMIC_DRAW);
}

void Engine::render() {

	glClear(GL_COLOR_BUFFER_BIT);
	glUseProgram(shader);
	glBindBufferRange(GL_UNIFORM_BUFFER, blockIndex, UBO, 0, blockSize);

	glBindVertexArray(ourQuad->VAO);
	glDrawArrays(GL_TRIANGLES, 0, ourQuad->vertexCount);

}
