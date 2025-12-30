#pragma once
#include <vulkan/vulkan.hpp>

#include <GLFW/glfw3.h>

#include <iostream>
#include <vector>
#include <set>
#include <string>
#include <optional>
#include <fstream>
#include <sstream>
#include <unordered_map>
#include <random>

#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

//--------- Assets -------------//

enum class pipelineType {
	RAYTRACE
};

// String Processing functions

std::vector<std::string> split(std::string line, std::string delimiter);

// Random functions

inline float random_float();

inline float random_float(float min, float max);