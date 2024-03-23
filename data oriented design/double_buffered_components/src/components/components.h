#pragma once
#include "../config.h"

struct TransformComponent {
    glm::vec3 position;
    glm::vec3 eulers;
    float scale;
};

struct VelocityComponent {
    glm::vec3 angular;
};