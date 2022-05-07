#include "simple_component.h"

SimpleComponent::SimpleComponent(ComponentCreateInfo* createInfo) {
	this->position = createInfo->position;
	this->velocity = createInfo->velocity;
}

void SimpleComponent::update(float rate) {

	position += velocity * rate;

	modelTransform = glm::mat4(1.0f);
	modelTransform = glm::translate(modelTransform, position);
}