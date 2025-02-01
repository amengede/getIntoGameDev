#include "animation_system.h"

AnimationSystem::AnimationSystem(
	Animations& animationSet, 
	ComponentSet<Animation>& animations, 
	ComponentSet<Skeleton>& skeletons) :
	skeletons(skeletons),
	animationSet(animationSet),
	animations(animations) {
}

void AnimationSystem::update() {

	for (size_t i = 0; i < animations.components.size(); ++i) {

		uint32_t id = animations.entities[i];
		Animation& animation = animations.components[i];
		Skeleton& skeleton = skeletons.get_component(id);

		for (Playhead& playhead : animation.playheads) {

			KeyframeSpan& animator = animationSet.spans[playhead.span];
			BoneComponent& bone = skeleton.bones[animator.target];
			
			float t = static_cast<float>(playhead.t) / static_cast<float>(animator.length);
			bone.rotation = (1.0f - t) * animator.rotation_a + t * animator.rotation_b;

			playhead.t += 1;

			if (playhead.t >= animator.length) {
				playhead.t = 0;
				playhead.span = animator.next;
			}
		}
	}
}