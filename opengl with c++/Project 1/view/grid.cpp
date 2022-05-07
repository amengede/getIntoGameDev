#include "grid.h"

Grid::Grid(int size) {

	std::vector<float> vertices(12 * size * size);

	for (int i = 0; i < size; ++i) {
		vertices.push_back(i);
		vertices.push_back(0);
		vertices.push_back(0);

		vertices.push_back(i);
		vertices.push_back(size - 1);
		vertices.push_back(0);
	}
	for (int i = 0; i < size; ++i) {
		vertices.push_back(0);
		vertices.push_back(i);
		vertices.push_back(0);

		vertices.push_back(size - 1);
		vertices.push_back(i);
		vertices.push_back(0);
	}
	vertexCount = int(vertices.size()) / 3;
	glCreateBuffers(1, &VBO);
	glCreateVertexArrays(1, &VAO);
	glVertexArrayVertexBuffer(VAO, 0, VBO, 0, 3 * sizeof(float));
	glNamedBufferStorage(
		VBO, vertices.size() * sizeof(float), vertices.data(), GL_DYNAMIC_STORAGE_BIT);
	//pos: 0
	glEnableVertexArrayAttrib(VAO, 0);
	glVertexArrayAttribFormat(VAO, 0, 3, GL_FLOAT, GL_FALSE, 0);
	glVertexArrayAttribBinding(VAO, 0, 0);
}

Grid::~Grid() {
	glDeleteBuffers(1, &VBO);
	glDeleteVertexArrays(1, &VAO);
}