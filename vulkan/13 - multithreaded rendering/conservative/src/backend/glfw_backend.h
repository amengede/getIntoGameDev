#pragma once
#include <GLFW/glfw3.h>

/**
 * @brief Build a window for our app.
 *
 * @param width width of the window in pixels
 * @param height height of the window in pixels
 * @param name name of the window
 * @return GLFWwindow* The created window
 */
GLFWwindow* build_window(int width, int height, const char* name);