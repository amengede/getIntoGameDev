#include "camera.h"
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glad/glad.h>
#include <glm/gtc/type_ptr.hpp>

CameraSystem::CameraSystem(uint32_t shader) {

	this->shader = shader;
	position = glm::vec3(0.0f, 0.0f, 0.0f);
	eulers = glm::vec3(0.0f, 0.0f, 0.0f);
	forwards = glm::vec3(1.0f, 0.0f, 0.0f);
	right = glm::vec3(0.0f, 0.0f, 0.0f);
	up = glm::vec3(0.0f, 0.0f, 0.0f);

	constexpr float fovY = glm::radians(45.0f);
	float aspect = windowWidth / windowHeight;
	float near = 0.1f;
	float far = 200.0f;
	
	projection = glm::perspective(fovY, aspect, near, far);
	/*
	std::cout << "----" << std::endl;
	for (int i = 0; i < 4; ++i) {
		for (int j = 0; j < 4; ++j) {
			std::cout << projection[i][j] << ", ";
		}
		std::cout << std::endl;
	}
	*/
	viewProjLocation = glGetUniformLocation(shader, "viewProj");

	//std::cout << "\Eye: <" << position.x << ", " << position.y << ", " << position.z << ">" << std::endl;
}

void CameraSystem::update() {

	forwards = {
		glm::cos(glm::radians(eulers.z)) * glm::cos(glm::radians(eulers.y)),
		glm::sin(glm::radians(eulers.z)) * glm::cos(glm::radians(eulers.y)),
		glm::sin(glm::radians(eulers.y)) };

	right = glm::normalize(glm::cross(forwards, glm::vec3(0.0f, 0.0f, 1.0f)));

	up = glm::normalize(glm::cross(right, forwards));

	glm::mat4 viewProj = projection * glm::lookAt(position, position + forwards, up);
	/*
	std::cout << "---- Camera Data ----" << std::endl;

	std::cout << "\tForwards: <" << forwards.x << ", " << forwards.y << ", " << forwards.z << ">" << std::endl;
	std::cout << "\tRight: <" << right.x << ", " << right.y << ", " << right.z << ">" << std::endl;
	std::cout << "\tUp: <" << up.x << ", " << up.y << ", " << up.z << ">" << std::endl;

	std::cout << "\Eye: <" << position.x << ", " << position.y << ", " << position.z << ">" << std::endl;
	std::cout << "\tCenter: <" << (position + forwards).x << ", " << (position + forwards).y << ", " << (position + forwards).z << ">" << std::endl;
	std::cout << "\tUp: <" << up.x << ", " << up.y << ", " << up.z << ">" << std::endl;

	std::cout << "Resulting view matrix:" << std::endl;
	for (int i = 0; i < 4; ++i) {
		for (int j = 0; j < 4; ++j) {
			std::cout << view[i][j] << ", ";
		}
		std::cout << std::endl;
	}
	*/

	glUniformMatrix4fv(viewProjLocation, 1, GL_FALSE, glm::value_ptr(viewProj));

}

void CameraSystem::move(glm::vec3 dPos) {

	position += forwards * dPos.x;
	position += right * dPos.y;
	position += up * dPos.z;
	//std::cout << "\Eye: <" << position.x << ", " << position.y << ", " << position.z << ">" << std::endl;
}

void CameraSystem::spin(glm::vec3 dEulers) {
	
	eulers.z += dEulers.z;
	if (eulers.z > 360.0f) {
		eulers.z -= 360.0f;
	}
	if (eulers.z < 0.0f) {
		eulers.z += 360.0f;
	}

	eulers.y = std::min(89.0f, std::max(-89.0f, eulers.y + dEulers.y));
}
