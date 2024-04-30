#include "scene.h"

Scene::Scene() {

	build_raycasting_environment();

}

void Scene::update() {

	description.forwards = { player.forwards[0], player.forwards[1] };
	description.right = { player.right[0], player.right[1] };
	description.position = { player.position[0], player.position[1] };
	description.wallCount = 67;
}

void Scene::build_raycasting_environment() {
	//Walls!!!
	walls.reserve(67);
	std::vector<glm::vec4> geometryData = { {
		{9, 26, 12, 26},  {12, 26, 12, 27}, {12, 28, 12, 29}, {12, 29, 9, 29},
		{9, 29, 9, 26},   {12, 27, 16, 27}, {16, 28, 12, 28}, {17, 27, 17, 28},
		{16, 27, 16, 23}, {17, 23, 17, 27}, {17, 28, 17, 32}, {16, 32, 16, 28},
		{16, 23, 12, 23}, {12, 22, 16, 22}, {20, 23, 17, 23}, {17, 22, 20, 22},
		{17, 18, 17, 22}, {16, 22, 16, 18}, {16, 18, 13, 18}, {13, 18, 13, 5},
		{13, 5, 20, 5},   {20, 5, 20, 18},  {20, 18, 17, 18}, {12, 23, 12, 25},
		{12, 25, 3, 25},  {3, 25, 3, 19},   {3, 19, 12, 19},  {12, 19, 12, 22},
		{20, 22, 20, 20}, {20, 20, 24, 20}, {24, 20, 24, 13}, {24, 13, 29, 13},
		{29, 13, 29, 10}, {29, 10, 34, 10}, {34, 10, 34, 18}, {34, 18, 29, 18},
		{29, 18, 29, 15}, {29, 15, 26, 15}, {26, 15, 26, 20}, {26, 20, 26, 25},
		{26, 25, 20, 25}, {20, 25, 20, 23}, {17, 32, 25, 32}, {25, 32, 25, 42},
		{25, 42, 8, 42}	, {8, 42, 8, 32},   {8, 32, 16, 32}	, {23, 34, 22, 34},
		{22, 34, 22, 37}, {22, 37, 23, 37}, {23, 37, 23, 34}, {20, 34, 19, 34},
		{19, 34, 19, 37}, {19, 37, 20, 37}, {20, 37, 20, 34}, {17, 34, 16, 34},
		{16, 34, 16, 37}, {16, 37, 17, 37}, {17, 37, 17, 34}, {14, 34, 13, 34},
		{13, 34, 13, 37}, {13, 37, 14, 37}, {14, 37, 14, 34}, {11, 34, 10, 34},
		{10, 34, 10, 37}, {10, 37, 11, 37}, {11, 37, 11, 34}
	} };

	for (int i = 0; i < 67; ++i) {

		glm::vec4 data{ geometryData[i] };
		float x1{ data[0]};
		float y1{ data[1] };
		float x2{ data[2] };
		float y2{ data[3] };

		glm::vec3 position = { x1, y1, 1.0f };
		glm::vec3 endPoint = { x2, y2, 1.0f };
		glm::vec3 direction = endPoint - position;

		glm::vec3 direction_a, direction_b;
		direction_a[0] = x2 - x1;
		direction_a[1] = y2 - y1;
		direction_a[2] = 1.0f;

		direction_b[0] = x2 - x1;
		direction_b[1] = y2 - y1;
		direction_b[2] = 0.0f;

		glm::vec3 normal = glm::normalize(glm::cross(direction_a, direction_b));

		float r = 0.5f * (i % 2) + 0.5f;
		float g = 0.25f * (i % 4) + 0.25f;
		float b = 0.125f * (i % 8) + 0.125f;
		glm::vec4 color = glm::vec4(r, g, b, 1.0f);

		glm::vec2 pos = { x1, y1 };
		glm::vec2 n = { normal[0], normal[1] };
		glm::vec2 d = { direction[0], direction[1] };
		walls.push_back({ pos, n, d, color });
	}
}