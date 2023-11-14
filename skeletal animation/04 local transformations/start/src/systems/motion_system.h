#pragma once
#include "../config.h"
#include "../components/components.h"
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