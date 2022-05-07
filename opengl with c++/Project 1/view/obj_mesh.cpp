#include "obj_mesh.h"

ObjMesh::ObjMesh(MeshCreateInfo* createInfo) {

	std::vector<float> vertices = 
		util::load_model_from_file(createInfo->filename, createInfo->preTransform);
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

ObjMesh::~ObjMesh() {
	glDeleteBuffers(1, &VBO);
	glDeleteVertexArrays(1, &VAO);
}