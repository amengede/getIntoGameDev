#pragma once
#include <glm/glm.hpp>
#include <unordered_map>
#include <string>

struct Mesh {
    uint32_t elementCount, VAO, VBO, EBO;
};

constexpr uint32_t grid_count = 100;

constexpr float windowWidth = 1920.0f;
constexpr float windowHeight = 1080.0f;