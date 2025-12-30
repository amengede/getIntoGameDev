#include "skeletal_system.h"

SkeletalSystem::SkeletalSystem(ComponentSet<Skeleton>& skeletons):
skeletons(skeletons){

}

void SkeletalSystem::update() {

	for (Skeleton& skeleton : skeletons.components) {
		//Assuming the root is at index 0
		BoneComponent& root = skeleton.bones[0];
		for (unsigned int childIndex : root.children) {
			SkeletalSystem::update_bone(skeleton, childIndex, glm::mat4(1.0f));
		}
	}
}

void SkeletalSystem::update_bone(Skeleton& skeleton, unsigned int index, glm::mat4 parentTransform) {
	BoneComponent& bone = skeleton.bones[index];
	glm::vec3 tempPos = glm::vec3(parentTransform * glm::vec4(bone.position, 1.0f));

	glm::mat4 modelToBone = glm::translate(glm::mat4(1.0f), -tempPos);
	glm::mat4 rotatation = glm::mat4_cast(bone.rotation);
	glm::mat4 boneToModel = glm::translate(glm::mat4(1.0f), tempPos);

	bone.transform = boneToModel * rotatation * modelToBone * parentTransform;

	for (unsigned int childIndex : bone.children) {
		SkeletalSystem::update_bone(skeleton, childIndex, bone.transform);
	}
}