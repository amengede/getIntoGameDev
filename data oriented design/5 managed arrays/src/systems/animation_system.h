#pragma once
#include "../config.h"
#include "../components/animation_component.h"
#include "../components/component_set.h"

class AnimationSystem {
public:
    
    void update(
        ComponentSet<AnimationComponent>& animationComponents,
        float frameTime);
};