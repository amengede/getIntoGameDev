#pragma once
#include "../config.h"
#include "../components/components.h"
#include "../components/component_set.h"

class SkeletalSystem {
public:

    SkeletalSystem(ComponentSet<Skeleton>& skeletons);

    void update();

private:

    void update_bone(Skeleton& skeleton, unsigned int index, glm::mat4 parentTransform);

    ComponentSet<Skeleton>& skeletons;
};