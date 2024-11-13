#include "motion_system.h"

void MotionSystem::update(
    ComponentSet<TransformComponent> &transformComponents,
    ComponentSet<PhysicsComponent> &physicsComponents,
    float dt) {
    
    for (size_t i = 0; i < physicsComponents.entities.size(); ++i) {

        uint32_t& entity = physicsComponents.entities[i];
        PhysicsComponent& physicsComponent = physicsComponents.components[i];
        TransformComponent& transform = transformComponents.get_component(entity);

        transform.position += physicsComponent.velocity * dt;
        transform.eulers += physicsComponent.eulerVelocity * dt;
        if (transform.eulers.z > 360) {
            transform.eulers.z -= 360;
        }
    }
}