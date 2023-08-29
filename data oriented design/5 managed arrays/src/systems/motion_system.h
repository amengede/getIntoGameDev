#pragma once
#include "../config.h"
#include "../components/transform_component.h"
#include "../components/physics_component.h"
#include "../components/component_set.h"

class MotionSystem {
    public:
    
    void update(
        ComponentSet<TransformComponent> &transformComponents,
        ComponentSet<PhysicsComponent> &physicsComponents,
        float dt);
};