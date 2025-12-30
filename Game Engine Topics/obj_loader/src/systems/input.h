#pragma once
#include "../config.h"
#include <GLFW/glfw3.h>
#include "../components/registry.h"
class InputSystem {
public:
	InputSystem(GLFWwindow* window);
	std::unordered_map<int, bool> keys;
private:
	void key_callback(GLFWwindow* window, int key, int scancode, int action, int mods);
	void mouse_button_callback(GLFWwindow* window, int button, int action, int mods);
};