#include "quad_model.h"

QuadModel::QuadModel() {

	//Make Cube
	//x,y,s,t
	std::vector<float> vertices = { {
		-1, -1, 0.0f, 0.0f, // bottom
		 1, -1, 1.0f, 0.0f,
		 1,  1, 1.0f, 1.0f,

		 1,  1, 1.0f, 1,
		-1,  1, 0.0f, 1,
		-1, -1, 0.0f, 0,
	} };

	vertexCount = 6;
	glCreateBuffers(1, &VBO);
	glCreateVertexArrays(1, &VAO);
	glVertexArrayVertexBuffer(VAO, 0, VBO, 0, 4 * sizeof(float));
	glNamedBufferStorage(VBO, vertices.size() * sizeof(float), vertices.data(), GL_DYNAMIC_STORAGE_BIT);
	glEnableVertexArrayAttrib(VAO, 0);
	glEnableVertexArrayAttrib(VAO, 1);
	glVertexArrayAttribFormat(VAO, 0, 2, GL_FLOAT, GL_FALSE, 0);
	glVertexArrayAttribFormat(VAO, 1, 2, GL_FLOAT, GL_FALSE, 2 * sizeof(float));
	glVertexArrayAttribBinding(VAO, 0, 0);
	glVertexArrayAttribBinding(VAO, 1, 0);
}

QuadModel::~QuadModel() {
	glDeleteBuffers(1, &VBO);
	glDeleteVertexArrays(1, &VAO);
}