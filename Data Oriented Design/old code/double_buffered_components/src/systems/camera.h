#pragma once
#include "../config.h"
#include "../components/registry.h"

class CameraSystem {
public:
	CameraSystem(uint32_t shader);
	void update();
	void move(glm::vec3 dPos);
	void spin(glm::vec3 dEulers);
private:

	glm::vec3 position, eulers, forwards, right, up;
	glm::uint32_t shader, viewProjLocation;
	glm::mat4 projection;
};