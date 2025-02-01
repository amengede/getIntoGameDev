#include "quadmesh.h"

QuadMesh::QuadMesh(float w, float h) {

	//x y r g b
	vertices = { {
			-w / 2, -h / 2, 1.0f, 0.0f, 0.0f,
			 w / 2, -h / 2, 0.0f, 1.0f, 0.0f,
			 w / 2,  h / 2, 0.0f, 0.0f, 1.0f,

			 w / 2,  h / 2, 0.0f, 0.0f, 1.0f,
			-w / 2,  h / 2, 1.0f, 0.0f, 1.0f,
			-w / 2, -h / 2, 1.0f, 0.0f, 0.0f
	} };

	vertexCount = 6;

	glCreateBuffers(1, &VBO);

	glCreateVertexArrays(1, &VAO);

	//(VAO, binding index, VBO, offset, stride)
	glVertexArrayVertexBuffer(VAO, 0, VBO, 0, 5 * sizeof(float));

	//(VBO, size in bytes, pointer to data start, mode)
	glNamedBufferStorage(VBO, vertices.size() * sizeof(float), vertices.data(), GL_DYNAMIC_STORAGE_BIT);


	glEnableVertexArrayAttrib(VAO, 0);
	glEnableVertexArrayAttrib(VAO, 1);
	//(VAO, location, size, type, should be normalized, (void*)offset)
	glVertexArrayAttribFormat(VAO, 0, 2, GL_FLOAT, GL_FALSE, 0);
	glVertexArrayAttribFormat(VAO, 1, 3, GL_FLOAT, GL_FALSE, 2 * sizeof(float));
	//(VAO, location, binding)
	glVertexArrayAttribBinding(VAO, 0, 0);
	glVertexArrayAttribBinding(VAO, 1, 0);
}

QuadMesh::~QuadMesh(){
	glDeleteBuffers(1, &VBO);
	glDeleteVertexArrays(1, &VAO);
}