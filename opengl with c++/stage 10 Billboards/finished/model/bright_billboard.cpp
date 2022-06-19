#include "bright_billboard.h"

BrightBillboard::BrightBillboard(BrightbillboardCreateInfo* createInfo) {
	this->position = createInfo->position;
	this->color = createInfo->color;
	this->strength = createInfo->strength;
	modelTransform = glm::mat4(1.0f);
}

void BrightBillboard::update(glm::vec3 playerPosition) {

	glm::vec3 directionFromPlayer = position - playerPosition;
	float theta = glm::atan(directionFromPlayer.y, directionFromPlayer.x);
	float distance2D = glm::sqrt(
		directionFromPlayer.x * directionFromPlayer.x + directionFromPlayer.y * directionFromPlayer.y
	);
	float phi = glm::atan(-directionFromPlayer.z, distance2D);

	modelTransform = glm::mat4(1.0f);
	modelTransform = glm::translate(modelTransform, position);
	modelTransform = modelTransform
		* glm::eulerAngleXYZ(0.0f, 0.0f, theta)
		* glm::eulerAngleXYZ(0.0f, phi, 0.0f);

}