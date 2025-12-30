#pragma once
#include "../config.h"
#include "../components/components.h"
#include "../components/component_set.h"

class Factory {

public:
    Factory(
        ComponentSet<PhysicsComponent>& physicsComponents,
        ComponentSet<RenderComponent>& renderComponents,
        ComponentSet<TransformComponent>& transformComponents);
    
    ~Factory();

    void make_cube(glm::vec3 position, glm::vec3 eulers, 
        glm::vec3 eulerVelocity);

    PinComponent drop_pin();

private:

    unsigned int entities_made = 0;
    std::vector<unsigned int> garbage_bin;

    ComponentSet<PhysicsComponent>& physicsComponents;
    ComponentSet<RenderComponent>& renderComponents;
    ComponentSet<TransformComponent>& transformComponents;

    unsigned int allocate_id();

};