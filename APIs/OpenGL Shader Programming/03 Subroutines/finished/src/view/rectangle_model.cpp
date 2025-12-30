#include "rectangle_model.h"
#include <glad/glad.h>

RectangleModel::RectangleModel(RectangleModelCreateInfo* createInfo) {

	float l = createInfo->size.x / 2;
	float w = createInfo->size.y / 2;
	float h = createInfo->size.z / 2;

	//Make Cube
	//x,y,z,s,t
	std::vector<float> vertices = { {
		-l, -w, -h, 0.0f, 0.0f, // bottom
		 l, -w, -h, 1.0f, 0.0f,
		 l,  w, -h, 1.0f, 1.0f,

		 l,  w, -h, 1.0f, 1,
		-l,  w, -h, 0.0f, 1,
		-l, -w, -h, 0.0f, 0,

		-l, -w,  h, 0.0f, 0.0f, //top
		 l, -w,  h, 1.0f, 0.0f,
		 l,  w,  h, 1.0f, 1.0f,

		 l,  w,  h, 1.0f, 1.0f,
		-l,  w,  h, 0.0f, 1.0f,
		-l, -w,  h, 0.0f, 0.0f,

		-l,  w,  h, 1.0f, 0.0f, //left
		-l,  w, -h, 1.0f, 1.0f,
		-l, -w, -h, 0.0f, 1.0f,

		-l, -w, -h, 0.0f, 1.0f,
		-l, -w,  h, 0.0f, 0.0f,
		-l,  w,  h, 1.0f, 0.0f,

		 l,  w,  h, 1.0f, 0.0f, //right
		 l,  w, -h, 1.0f, 1.0f,
		 l, -w, -h, 0.0f, 1.0f,

		 l, -w, -h, 0.0f, 1.0f,
		 l, -w,  h, 0.0f, 0.0f,
		 l,  w,  h, 1.0f, 0.0f,

		-l, -w, -h, 0.0f, 1.0f, //back
		 l, -w, -h, 1.0f, 1.0f,
		 l, -w,  h, 1.0f, 0.0f,

		 l, -w,  h, 1.0f, 0.0f,
		-l, -w,  h, 0.0f, 0.0f,
		-l, -w, -h, 0.0f, 1.0f,

		-l,  w, -h, 0.0f, 1.0f, //front
		 l,  w, -h, 1.0f, 1.0f,
		 l,  w,  h, 1.0f, 0.0f,

		 l,  w,  h, 1.0f, 0.0f,
		-l,  w,  h, 0.0f, 0.0f,
		-l,  w, -h, 0.0f, 1.0f
	} };
	vertexCount = vertices.size() / 5;

	glGenBuffers(1, &VBO);
	glGenVertexArrays(1, &VAO);
	glBindVertexArray(VAO);
	glBindBuffer(GL_ARRAY_BUFFER, VBO);
	glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(float), vertices.data(), GL_STATIC_DRAW);

	glEnableVertexAttribArray(0);
	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, (void*)0);

	glEnableVertexAttribArray(1);
	glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, (void*)12);
}

RectangleModel::~RectangleModel() {
	glDeleteBuffers(1, &VBO);
	glDeleteVertexArrays(1, &VAO);
}
