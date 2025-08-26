#pragma once
#include "../config.h"

struct ParticleCreateInfo {
	glm::vec3 position, velocity, acceleration;
	float lifetime;
	glm::vec3 color;
};

class Particle {
public:
	glm::vec3 position, velocity, acceleration;
	glm::mat4 modelTransform;
	float t, lifetime;
	glm::vec3 color;
	glm::vec4 tint;
	Particle(ParticleCreateInfo* createInfo);
	void update(float rate);
};