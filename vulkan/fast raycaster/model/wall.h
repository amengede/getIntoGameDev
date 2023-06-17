#pragma once
#include "../config.h"
struct Wall {
	alignas(8) glm::vec2 position;
	alignas(8) glm::vec2 normal;
	alignas(16) glm::vec2 direction;
	alignas(16) glm::vec4 color;
};