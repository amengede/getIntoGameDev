#pragma once
#include "../config.h"
#include "components.h"
#include "component_set.h"
#include "double_buffered_set.h"

/*
    Basically holds all components in the game.
*/
struct ComponentRegistry {
    ComponentSet<TransformComponent> transforms;
    ComponentSet<VelocityComponent> velocities;
    DoubleBufferedComponentSet<std::vector<glm::vec3>> particlePositions;
    DoubleBufferedComponentSet<std::vector<glm::vec3>> particleVelocities;
    Mesh particlePoints, particleLines;
};