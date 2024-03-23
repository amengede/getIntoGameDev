#include "input.h"

InputSystem::InputSystem(GLFWwindow* window) {

	glfwSetWindowUserPointer(window, this);
	auto key_func = [](GLFWwindow* w, int key, int scancode, int action, int mods) {
		static_cast<InputSystem*>(glfwGetWindowUserPointer(w))->key_callback(w, key, scancode, action, mods);
	};
	glfwSetKeyCallback(window, key_func);

	auto mouse_func = [](GLFWwindow* w, int button, int action, int mods) {
		static_cast<InputSystem*>(glfwGetWindowUserPointer(w))->mouse_button_callback(w, button, action, mods);
		};
	glfwSetMouseButtonCallback(window, mouse_func);
}

void InputSystem::key_callback(GLFWwindow* window, int key, int scancode, int action, int mods) {

	bool state = action != GLFW_RELEASE;
	keys[key] = state;
}

void InputSystem::mouse_button_callback(GLFWwindow* window, int button, int action, int mods) {
}