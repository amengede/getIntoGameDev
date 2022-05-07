#include "player.h"

Player::Player(PlayerCreateInfo* createInfo) {
	this->position = createInfo->position;
	this->eulers = createInfo->eulers;
	velocity = glm::vec3(0.0f, 0.0f, 0.0f);
	state = STATE::FALLING_ON;
	health = 18;
	canShoot = true;
	reloadTime = 0.0f;
	fallTime = 0.0f;
}

void Player::update(float rate) {
	
	if (state == STATE::STABLE) {
		if (abs(velocity.y) < 0.01) {
			eulers.x *= 0.9;
			if (abs(eulers.x) < 0.5) {
				eulers.x = 0.0f;
			}
		}
		else {
			position += velocity * rate;
			eulers.x += 8 * velocity.y;

			position.y = std::min(6.0f, std::max(-6.0f, position.y));
			eulers.x = std::min(45.0f, std::max(-45.0f, eulers.x));
		}
		if (!canShoot) {
			reloadTime -= rate;
			if (reloadTime < 0) {
				reloadTime = 0;
				canShoot = true;
			}
		}
		if (health < 0) {
			state = STATE::FALLING_OFF;
		}
	}
	else if (state == STATE::FALLING_ON) {
		position.z = 0.99f + (glm::pow(0.9f, fallTime)) * 16;
		fallTime += rate;
		if (position.z < 1) {
			fallTime = 0;
			position.z = 1;
			state = STATE::STABLE;
		}
	}
	else {
		position.z = -8.0f + (glm::pow(0.9f, fallTime)) * 9;
		fallTime += rate;
	}
	modelTransform = glm::mat4(1.0f);
	modelTransform = glm::translate(modelTransform, position);
	modelTransform = modelTransform * glm::eulerAngleXYZ(
		glm::radians(eulers.x), glm::radians(eulers.y), glm::radians(eulers.z)
	);
}