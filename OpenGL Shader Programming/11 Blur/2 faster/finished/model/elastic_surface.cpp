#include "elastic_surface.h"

ElasticSurface::ElasticSurface(std::vector<glm::vec3> corners, glm::vec3 color) {

	controlPoints.reserve(16);
	controlPointVelocities.reserve(16);

	glm::vec3 top_left = corners[0];
	glm::vec3 bottom_right = corners[1];
	float length = bottom_right.x - top_left.x;
	float width = bottom_right.y - top_left.y;

	for (float y = 0; y < 4; ++y) {
		for (float x = 0; x < 4; ++x) {
			controlPoints.push_back(
				glm::vec3(
					top_left.x + length * x / 4.0f,
					top_left.y + width * y / 4.0f,
					top_left.y + width * y / 4.0f
				)
			);
			controlPointVelocities.push_back(
				glm::vec3(0.0f, 0.0f,0.0f)
			);
		}
	}

	this->color = color;
}

glm::vec3 ElasticSurface::TensionFromNeighbour(int x, int y, glm::vec3 position) {

	glm::vec3 otherPosition = controlPoints[x + 4 * y];

	return otherPosition - position;
}

void ElasticSurface::Update(float dt) {

	//For internal points:
	
	for (int x = 1; x < 3; ++x) {
		for (int y = 1; y < 3; ++y) {

			glm::vec3 net_force = glm::vec3(0.0f, 0.0f, -0.0025f);

			glm::vec3 position = controlPoints[x + 4 * y];

			glm::vec3 tension = TensionFromNeighbour(x - 1, y - 1, position);
			tension += TensionFromNeighbour(x, y - 1, position);
			tension += TensionFromNeighbour(x + 1, y - 1, position);
			tension += TensionFromNeighbour(x - 1, y, position);
			tension += TensionFromNeighbour(x + 1, y, position);
			tension += TensionFromNeighbour(x - 1, y + 1, position);
			tension += TensionFromNeighbour(x, y + 1, position);
			tension += TensionFromNeighbour(x + 1, y + 1, position);
			net_force += 0.0002f * tension;

			controlPointVelocities[x + 4 * y] += dt * net_force;
		}
	}
	

	for (int x = 1; x < 3; ++x) {
		for (int y = 1; y < 3; ++y) {

			controlPoints[x + 4 * y] += dt * controlPointVelocities[x + 4 * y];

		}
	}

}