#pragma once
#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <iostream>
#include <vector>
#include <array>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <glm/gtx/euler_angles.hpp>
#include <sstream>
#include <fstream>
#include <string>
#include <cstdlib>
#include <random>
#include <chrono>

inline float random_float();

inline float random_float(float min, float max);

inline glm::vec3 random_vec();

inline glm::vec3 random_vec(float min, float max);

glm::vec3 random_in_unit_sphere();