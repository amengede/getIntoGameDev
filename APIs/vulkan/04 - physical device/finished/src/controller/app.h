#pragma once
#include "../logging/logger.h"
#include <GLFW/glfw3.h>

/**
* @brief The main program.
*/
class App {
public:

	/**
	* @brief Construct a new app
	* 
	* @param window The main window for the program
	*/
	App(GLFWwindow* window);

private:

	/**
	* @brief run the program
	*/
	void main_loop();

	/**
	* @brief the main window for the program
	*/
	GLFWwindow* window;

	/**
	* @brief static debug logger
	*/
	Logger* logger;
};