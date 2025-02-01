#pragma once
#include "../config.h"

struct PhysicsComponent {
    glm::vec3 velocity;
    glm::vec3 eulerVelocity;
};

struct PinComponent {
    glm::vec3 position;
    glm::mat4 modelToPin;
    glm::mat4 localTransform;
    glm::mat4 pinToModel;
};

struct RenderComponent {
    ObjectType objectType;
};

struct TransformComponent {
    glm::vec3 position;
    glm::vec3 eulers;
};