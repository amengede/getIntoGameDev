/*---------------------------------------------------------------------------*/
/*	Controls high level logic.
/*---------------------------------------------------------------------------*/
#pragma once
#include <GLFW/glfw3.h>
#include "../renderer/renderer.h"

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
	App();

private:

	/**
	* @brief run the program
	*/
	void main_loop();

	/**
	* @brief the main window for the program
	*/
	GLFWwindow* window;

	Engine* engine;
};
/*---------------------------------------------------------------------------*/