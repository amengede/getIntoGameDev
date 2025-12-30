#pragma once
#include "../config.h"
#include "../components/components.h"
#include "../components/component_set.h"

class Factory {

public:
    Factory(
        ComponentSet<RenderComponent>& renderComponents,
        ComponentSet<TransformComponent>& transformComponents,
        ComponentSet<Skeleton>& skeletons,
        Animations& animationSet, ComponentSet<Animation>& animations);
    
    ~Factory();

    void make_legs(glm::vec3 position, glm::vec3 eulers);

private:

    unsigned int entities_made = 0;
    std::vector<unsigned int> garbage_bin;
;
    ComponentSet<RenderComponent>& renderComponents;
    ComponentSet<TransformComponent>& transformComponents;
    ComponentSet<Skeleton>& skeletons;
    Animations& animationSet;
    ComponentSet<Animation>& animations;

    unsigned int allocate_id();

};