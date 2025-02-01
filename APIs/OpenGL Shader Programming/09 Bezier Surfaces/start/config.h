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
#include <glm/gtx/hash.hpp>
#include <sstream>
#include <fstream>
#include <string>
#include <map>
#include <chrono>
#include <random>
#include <unordered_map>

struct image {
	unsigned char* pixels;
	int width, height, channels;
};