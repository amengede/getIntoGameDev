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

std::vector<std::string> split(std::string line, std::string delimiter);

enum class ObjectType {
    eBox,
    eGeometry,
    eRevy
};

enum class AnimationType {
    eNone,
    eRun,
};