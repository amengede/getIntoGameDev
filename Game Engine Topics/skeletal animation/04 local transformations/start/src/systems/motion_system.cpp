#include "motion_system.h"

MotionSystem::MotionSystem(
        ComponentSet<TransformComponent> &transforms,
        ComponentSet<PhysicsComponent> &velocities):
transforms(transforms),
velocities(velocities) {

}

void MotionSystem::update(float dt) {
    
    for (size_t i = 0; i < velocities.entities.size(); ++i) {

        uint32_t& entity = velocities.entities[i];
        PhysicsComponent& physicsComponent = velocities.components[i];
        TransformComponent& transform = transforms.get_component(entity);

        transform.position += physicsComponent.velocity * dt;
        transform.eulers += physicsComponent.eulerVelocity * dt;
        if (transform.eulers.z > 360) {
            transform.eulers.z -= 360;
        }
    }
}