#include "quadmesh.h"
#include <glad/glad.h>

QuadMesh::QuadMesh(float w, float h) {

	//x y s t
	vertices = { {
			-w / 2, -h / 2, 0.0f, 1.0f,
			 w / 2, -h / 2, 1.0f, 1.0f,
			 w / 2,  h / 2, 1.0f, 0.0f,

			 w / 2,  h / 2, 1.0f, 0.0f,
			-w / 2,  h / 2, 0.0f, 0.0f,
			-w / 2, -h / 2, 0.0f, 1.0f
	} };

	vertexCount = 6;

	glGenBuffers(1, &VBO);

	glGenVertexArrays(1, &VAO);

	//(VAO, binding index, VBO, offset, stride)
	glBindVertexArray(VAO);
	glBindBuffer(GL_ARRAY_BUFFER, VBO);

	//(VBO, size in bytes, pointer to data start, mode)
	glBufferData(GL_ARRAY_BUFFER, vertexCount * 16, vertices.data(), GL_STATIC_DRAW);

	glEnableVertexAttribArray(0);
	glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, (void*)0);

	glEnableVertexAttribArray(1);
	glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, (void*)8);
}

QuadMesh::~QuadMesh(){
	glDeleteBuffers(1, &VBO);
	glDeleteVertexArrays(1, &VAO);
}
