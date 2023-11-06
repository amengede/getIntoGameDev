#pragma once

#include <glad/glad.h>
#include <GLFW/glfw3.h>

#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>

#include <iostream>

#include <vector>
#include <unordered_map>

#include <fstream>
#include <sstream>
#include <string>

#include <random>

float random_float();

float random_float(float min, float max);

glm::vec3 random_vec();

glm::vec3 random_vec(float min, float max);