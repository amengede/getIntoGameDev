#pragma once
#include "../config.h"

namespace util {
	std::vector<float> load_model_from_file(const char* filename, glm::mat4 preTransform);
}