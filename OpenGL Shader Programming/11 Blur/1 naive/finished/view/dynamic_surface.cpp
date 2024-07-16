#include "dynamic_surface.h"

DynamicSurface::DynamicSurface() {

	vertexCount = 16;
	glCreateBuffers(1, &VBO);
	glCreateVertexArrays(1, &VAO);
	glVertexArrayVertexBuffer(VAO, 0, VBO, 0, 3 * sizeof(float));
	glNamedBufferStorage(
		VBO, 16 * 4 * 3, NULL, GL_DYNAMIC_STORAGE_BIT
	);
	//pos: 0
	glEnableVertexArrayAttrib(VAO, 0);
	glVertexArrayAttribFormat(VAO, 0, 3, GL_FLOAT, GL_FALSE, 0);
	glVertexArrayAttribBinding(VAO, 0, 0);
}

void DynamicSurface::build(const std::vector<glm::vec3>& data) {

	vertexCount = static_cast<uint32_t>(data.size());

	std::vector<float> vertices;
	vertices.reserve(3 * vertexCount);
	for (glm::vec3 vertex : data) {
		vertices.push_back(vertex.x);
		vertices.push_back(vertex.y);
		vertices.push_back(vertex.z);
	}
	glNamedBufferSubData(VBO, 0, vertices.size() * sizeof(float), vertices.data());

}

DynamicSurface::~DynamicSurface() {
	glDeleteBuffers(1, &VBO);
	glDeleteVertexArrays(1, &VAO);
}