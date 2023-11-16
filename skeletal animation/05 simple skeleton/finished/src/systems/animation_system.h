#pragma once
#include "../config.h"
#include "../components/components.h"
#include "../components/component_set.h"

class AnimationSystem {
public:

    AnimationSystem(Animations& animationSet, ComponentSet<Animation>& animations, ComponentSet<Skeleton>& skeletons);

    void update();

private:

    Animations& animationSet;
    ComponentSet<Animation>& animations;
    ComponentSet<Skeleton>& skeletons;
};