#include "player.h"
#include <math.h>

Player::Player(float x, float y, float theta) {

	this->theta = theta;

	position = { x, y, 1.0f };
	forwards = {
		glm::cos(glm::radians(theta)),
		glm::sin(glm::radians(theta)),
		0.0f
	};
	right = {
		glm::cos(glm::radians(theta - 90)),
		glm::sin(glm::radians(theta - 90)),
		0.0f
	};
	up = {
		0,
		0,
		1
	};

}

void Player::spin(float dTheta) {

	theta = theta + dTheta;
	if (theta > 360) {
		theta -= 360;
	}
	else if (theta < 0) {
		theta += 360;
	}

	forwards = {
		glm::cos(glm::radians(theta)),
		glm::sin(glm::radians(theta)),
		0.0f
	};
	right = {
		glm::cos(glm::radians(theta - 90)),
		glm::sin(glm::radians(theta - 90)),
		0.0f
	};
}