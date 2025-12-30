#include "obj_mesh.h"
#include "obj_loader.h"
#include <glad/glad.h>

ObjMesh::ObjMesh(MeshCreateInfo* createInfo) {

	std::vector<float> vertices = 
		util::load_model_from_file(createInfo->filename, createInfo->preTransform);
	vertexCount = int(vertices.size()) / 8;

	//pos: 0, texcoord: 1, normal: 2
	glGenBuffers(1, &VBO);
	glGenVertexArrays(1, &VAO);
	glBindVertexArray(VAO);
	glBindBuffer(GL_ARRAY_BUFFER, VBO);
	glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(float), vertices.data(), GL_STATIC_DRAW);

	glEnableVertexAttribArray(0);
	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, (void*)0);

	glEnableVertexAttribArray(1);
	glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, (void*)12);

	glEnableVertexAttribArray(2);
	glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, (void*)20);
}

ObjMesh::~ObjMesh() {
	glDeleteBuffers(1, &VBO);
	glDeleteVertexArrays(1, &VAO);
}
