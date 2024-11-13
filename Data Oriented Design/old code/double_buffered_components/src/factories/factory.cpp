#include "factory.h"
#include <glad/glad.h>

Factory::Factory(ComponentRegistry& componentRegistry, uint32_t& shader):
componentRegistry(componentRegistry),
shader(shader) {}

unsigned int Factory::allocate_id() {
    
	if (garbage_bin.size() > 0) {
		uint32_t id = garbage_bin[garbage_bin.size() - 1];
		garbage_bin.pop_back();
		return id;
	}
	else {
		uint32_t id = entities_made++;
		return id;
	}
}

void Factory::make_mesh() {

	unsigned int id = allocate_id();

	const float radius = 2.0f;
	const float grid_size = 2.0f * radius / static_cast<float>(grid_count);
	std::vector<glm::vec3> points;
	points.resize(grid_count * grid_count);
	std::vector<glm::vec3> velocities;
	velocities.resize(grid_count * grid_count);

	std::vector<uint32_t> pointIndices;
	pointIndices.resize(grid_count * grid_count);
	std::vector<uint32_t> lineIndices;
	lineIndices.reserve(4 * (grid_count - 1) * grid_count);

	glm::vec3 minPoint = glm::vec3(0.0f, -radius / 2.0f, -radius / 2.0f);

	//Points
	for (uint32_t j = 0; j < grid_count; ++j) {
		for (uint32_t i = 0; i < grid_count; ++i) {
			points[grid_count * i + j] = minPoint + glm::vec3(0.0f, grid_size * j, grid_size * i);
			pointIndices[grid_count * i + j] = grid_count * i + j;
		}
	}

	//horizontal lines
	for (uint32_t i = 0; i < grid_count; ++i) {
		for (uint32_t j = 0; j < (grid_count - 1); ++j) {
			lineIndices.push_back(grid_count * i + j);
			lineIndices.push_back(grid_count * i + j + 1);
		}
	}

	//vertical lines
	for (uint32_t j = 0; j < grid_count; ++j) {
		for (uint32_t i = 0; i < (grid_count - 1); ++i) {
			lineIndices.push_back(grid_count * i + j);
			lineIndices.push_back(grid_count * (i + 1) + j);
		}
	}

	//Build everything
	glGenVertexArrays(1, &componentRegistry.particlePoints.VAO);
	glBindVertexArray(componentRegistry.particlePoints.VAO);

	glGenBuffers(1, &componentRegistry.particlePoints.VBO);
	glBindBuffer(GL_ARRAY_BUFFER, componentRegistry.particlePoints.VBO);
	glBufferData(GL_ARRAY_BUFFER, points.size() * sizeof(glm::vec3),
		NULL, GL_DYNAMIC_DRAW);
	//position
	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, (void*)0);
	glEnableVertexAttribArray(0);

	glGenBuffers(1, &componentRegistry.particlePoints.EBO);
	glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, componentRegistry.particlePoints.EBO);
	glBufferData(GL_ELEMENT_ARRAY_BUFFER,
		pointIndices.size() * sizeof(uint32_t),
		pointIndices.data(), GL_STATIC_DRAW);


	componentRegistry.particlePoints.elementCount = pointIndices.size();

	glGenVertexArrays(1, &componentRegistry.particleLines.VAO);
	glBindVertexArray(componentRegistry.particleLines.VAO);

	glGenBuffers(1, &componentRegistry.particleLines.VBO);
	glBindBuffer(GL_ARRAY_BUFFER, componentRegistry.particleLines.VBO);
	glBufferData(GL_ARRAY_BUFFER, points.size() * sizeof(glm::vec3),
		NULL, GL_DYNAMIC_DRAW);
	//position
	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, (void*)0);
	glEnableVertexAttribArray(0);

	glGenBuffers(1, &componentRegistry.particleLines.EBO);
	glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, componentRegistry.particleLines.EBO);
	glBufferData(GL_ELEMENT_ARRAY_BUFFER,
		lineIndices.size() * sizeof(uint32_t),
		lineIndices.data(), GL_STATIC_DRAW);


	componentRegistry.particleLines.elementCount = lineIndices.size();

	componentRegistry.particlePositions.insert(id, points);

	componentRegistry.particleVelocities.insert(id, velocities);
}