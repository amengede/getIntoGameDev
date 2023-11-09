#pragma once
#include "../config.h"
#include "../components/transform_component.h"
#include "../components/physics_component.h"
#include "../components/component_set.h"

class MotionSystem {
public:

    MotionSystem(
        ComponentSet<TransformComponent> &transforms,
        ComponentSet<PhysicsComponent> &velocities);
    
    void update(float dt);
    
private:
    ComponentSet<TransformComponent> &transforms;
    ComponentSet<PhysicsComponent> &velocities;

};