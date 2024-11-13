#include "animation_system.h"
    
void AnimationSystem::update(
    ComponentSet<AnimationComponent>& animationComponents,
    float frameTime) {
    
    for (AnimationComponent& animation : animationComponents.components) {
        animation.frame += animation.speed * frameTime / 16.667f;

        if (animation.frame >= animation.frameCount) {
            animation.frame -= animation.frameCount;
        }
    }
}