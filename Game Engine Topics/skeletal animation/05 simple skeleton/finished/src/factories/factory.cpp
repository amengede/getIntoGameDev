#include "factory.h"

Factory::Factory(
    ComponentSet<RenderComponent>& renderComponents,
    ComponentSet<TransformComponent>& transformComponents,
	ComponentSet<Skeleton>& skeletons, 
	Animations& animationSet, ComponentSet<Animation>& animations):
renderComponents(renderComponents),
transformComponents(transformComponents),
skeletons(skeletons),
animationSet(animationSet),
animations(animations){

	//Build animators for legs
	KeyframeSpan span;
	span.length = 60;
	span.rotation_a = glm::angleAxis(glm::radians(45.0f), glm::vec3(0.0f, 0.0f, 1.0f));
	span.rotation_b = glm::angleAxis(glm::radians(-45.0f), glm::vec3(0.0f, 0.0f, 1.0f));
	span.target = 1;
	span.next = 1;
	animationSet.spans.push_back(span);
	span.rotation_a = glm::angleAxis(glm::radians(-45.0f), glm::vec3(0.0f, 0.0f, 1.0f));
	span.rotation_b = glm::angleAxis(glm::radians(45.0f), glm::vec3(0.0f, 0.0f, 1.0f));
	span.next = 0;
	animationSet.spans.push_back(span);

	span.rotation_a = glm::angleAxis(glm::radians(45.0f), glm::vec3(0.0f, 0.0f, 1.0f));
	span.rotation_b = glm::angleAxis(glm::radians(-45.0f), glm::vec3(0.0f, 0.0f, 1.0f));
	span.target = 2;
	span.next = 3;
	animationSet.spans.push_back(span);
	span.rotation_a = glm::angleAxis(glm::radians(-45.0f), glm::vec3(0.0f, 0.0f, 1.0f));
	span.rotation_b = glm::angleAxis(glm::radians(45.0f), glm::vec3(0.0f, 0.0f, 1.0f));
	span.next = 2;
	animationSet.spans.push_back(span);
}

unsigned int Factory::allocate_id() {
        
	if (garbage_bin.size() > 0) {
		uint32_t id = garbage_bin[garbage_bin.size() - 1];
		garbage_bin.pop_back();
		return id;
	}
	else {
		return entities_made++;
	}
}

void Factory::make_legs(glm::vec3 position, glm::vec3 eulers) {

	unsigned int id = allocate_id();

	TransformComponent transform;
	transform.position = position;
	transform.eulers = eulers;
	transformComponents.insert(id, transform);
	
	RenderComponent render;
	render.objectType = ObjectType::eLegs;
	renderComponents.insert(id, render);

	//Root
	BoneComponent bone;
	bone.position = glm::vec3(0.0f);
	bone.rotation = glm::quat(glm::vec3(0.0f));
	bone.transform = glm::mat4(1.0f);
	bone.children.push_back(1);
	bone.children.push_back(2);
	Skeleton skeleton;
	skeleton.bones.push_back(bone);

	//Children 1 & 2
	bone.rotation = glm::angleAxis(glm::radians(45.0f), glm::vec3(0.0f, 0.0f, 1.0f));
	bone.children.clear();
	bone.children.push_back(3);
	skeleton.bones.push_back(bone);
	bone.rotation = glm::angleAxis(glm::radians(-45.0f), glm::vec3(0.0f, 0.0f, 1.0f));
	bone.children.clear();
	bone.children.push_back(4);
	skeleton.bones.push_back(bone);

	//Children 3 & 4
	bone.rotation = glm::angleAxis(glm::radians(-10.0f), glm::vec3(0.0f, 0.0f, 1.0f));
	bone.position = glm::vec3(0.0f, -0.5f, 0.0f);
	bone.children.clear();
	skeleton.bones.push_back(bone);
	skeleton.bones.push_back(bone);

	skeletons.insert(id, skeleton);

	//Apply animation to each bone
	Animation legAnimators;
	Playhead playhead;
	playhead.t = 0;
	playhead.span = 0;
	legAnimators.playheads.push_back(playhead);
	playhead.span = 3;
	legAnimators.playheads.push_back(playhead);
	animations.insert(id, legAnimators);
}