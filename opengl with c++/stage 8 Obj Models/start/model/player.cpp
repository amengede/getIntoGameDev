#include "player.h"

Player::Player(PlayerCreateInfo* createInfo) {
	this->position = createInfo->position;
	this->eulers = createInfo->eulers;
}

void Player::update() {
	forwards = {
			glm::sin(glm::radians(eulers.y)) * glm::cos(glm::radians(eulers.z)),
			glm::sin(glm::radians(eulers.y)) * glm::sin(glm::radians(eulers.z)),
			glm::cos(glm::radians(eulers.y))
	};
	glm::vec3 globalUp{ 0.0f, 0.0f, 1.0f };
	right = glm::cross(forwards, globalUp);
	up = glm::cross(right,forwards);
}