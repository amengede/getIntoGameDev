#include "light.h"

Light::Light(LightCreateInfo* createInfo) {
	this->position = createInfo->position;
	this->color = createInfo->color;
	this->strength = createInfo->strength;
}