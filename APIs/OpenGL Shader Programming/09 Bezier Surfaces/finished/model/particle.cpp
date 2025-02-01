#include "particle.h"

Particle::Particle(ParticleCreateInfo* createInfo) {

	this->position = createInfo->position;
	this->velocity = createInfo->velocity;
	this->acceleration = createInfo->acceleration;
	modelTransform = glm::mat4(1.0f);
	modelTransform = glm::translate(modelTransform, position);

	this->color = createInfo->color;
	this->lifetime = createInfo->lifetime;
	t = 0.0f;
	
}

void Particle::update(float rate) {
	
	velocity += rate * acceleration;
	position += rate * velocity;
	if (position.z < 0) {
		velocity.z *= -0.5f;
		position.z = 0.0f;
	}

	modelTransform = glm::mat4(1.0f);
	modelTransform = glm::translate(modelTransform, position);

	t += rate;
	tint = glm::vec4(color, 1.0f - (t / lifetime));

}