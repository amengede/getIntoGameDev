#include "world.h"
#include <glad/glad.h>

World::World(ComponentRegistry& componentRegistry):
	componentRegistry(componentRegistry) {}

void World::update(float frametime) {
	
	std::vector<glm::vec3>& oldPositions = componentRegistry.particlePositions.get_a_buffer().components[0];
	std::vector<glm::vec3>& newPositions = componentRegistry.particlePositions.get_b_buffer().components[0];
	
	std::vector<glm::vec3>& oldVelocities = componentRegistry.particleVelocities.get_a_buffer().components[0];
	std::vector<glm::vec3>& newVelocities = componentRegistry.particleVelocities.get_b_buffer().components[0];

	const float springConstant = 1000.0f;
	const float eq_length = 0.0f;

	for (uint32_t i = 1; i < grid_count - 1; ++i) {
		for (uint32_t j = 1; j < grid_count - 1; ++j) {

			glm::vec3 oldPos = oldPositions[grid_count * i + j];
			glm::vec3 net_force = glm::vec3(1.0f, 0.0f, -1.0f);

			//left
			glm::vec3 displacement = oldPositions[grid_count * i + j - 1] - oldPos;
			float length = glm::length(displacement);
			net_force += springConstant * (length - eq_length) * glm::normalize(displacement);
			//right
			displacement = oldPositions[grid_count * i + j + 1] - oldPos;
			length = glm::length(displacement);
			net_force += springConstant * (length - eq_length) * glm::normalize(displacement);
			//above
			displacement = oldPositions[grid_count * (i + 1) + j] - oldPos;
			length = glm::length(displacement);
			net_force += springConstant * (length - eq_length) * glm::normalize(displacement);
			//below
			displacement = oldPositions[grid_count * (i - 1) + j] - oldPos;
			length = glm::length(displacement);
			net_force += springConstant * (length - eq_length) * glm::normalize(displacement);

			newVelocities[grid_count * i + j] = (oldVelocities[grid_count * i + j] + (frametime / 1000.0f) * net_force);
			newPositions[grid_count * i + j] = oldPos + (frametime / 1000.0f) * newVelocities[grid_count * i + j];
		}
	}
	
	glBindVertexArray(componentRegistry.particleLines.VAO);
	glBindBuffer(GL_ARRAY_BUFFER, componentRegistry.particleLines.VBO);
	glBufferData(GL_ARRAY_BUFFER, newPositions.size() * sizeof(glm::vec3), newPositions.data(), GL_DYNAMIC_DRAW);
	
	glBindVertexArray(componentRegistry.particlePoints.VAO);
	glBindBuffer(GL_ARRAY_BUFFER, componentRegistry.particlePoints.VBO);
	glBufferData(GL_ARRAY_BUFFER, newPositions.size() * sizeof(glm::vec3), newPositions.data(), GL_DYNAMIC_DRAW);
	
	componentRegistry.particlePositions.flip();
	componentRegistry.particleVelocities.flip();
	
}