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
	glBindVertexArray(VAO);
	glBindBuffer(GL_ARRAY_BUFFER, VBO);

	glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(float), vertices.data(), GL_STATIC_DRAW);

	glEnableVertexAttribArray(0);
	glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, (void*)0);

	glEnableVertexAttribArray(1);
	glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, (void*)8);
}

QuadMesh::~QuadMesh(){
	glDeleteBuffers(1, &VBO);
	glDeleteVertexArrays(1, &VAO);
}
