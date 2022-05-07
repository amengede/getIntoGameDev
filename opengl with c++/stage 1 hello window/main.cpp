/*
	glad complains if OpenGL has already been included,
	so either we include glad ahead of glfw, 
	or 
	#define GLFW_INCLUDE_NONE
*/
#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <iostream>

//handles key presses
void processInput(GLFWwindow* window) {
	if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS) {
		glfwSetWindowShouldClose(window, true);
	}
}

int main() {
	glfwInit();

	//indicate to glfw that we want to make an OpenGL 4.5 context, in core mode
	glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
	glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 5);
	glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

	/*
		create a window:

		glfwCreateWindow(width, height, title, monitor for fullscreen, window to share with)

		creates a window and returns a pointer to it, returns NULL on failure
	*/
	GLFWwindow* window = glfwCreateWindow(640, 480, "This is working I hope", NULL, NULL);
	if (!window) {
		std::cout << "Window creation failed\n";
		glfwTerminate();
		return -1;
	}
	//OpenGL context has been created, make it the main context
	glfwMakeContextCurrent(window);

	/*
		initialize glad:

		gladLoadGLLoader(GLADloadproc& loadFunction)
		returns NULL on failure
	*/
	if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
		std::cout << "GLAD initialization failed\n";
		glfwTerminate();
		return -1;
	}

	//after glad has found process addresses, we can use OpenGL functions
	glViewport(0, 0, 640, 480);

	//game loop
	while (!glfwWindowShouldClose(window)) {

		processInput(window);

		//double buffer render flip
		glfwSwapBuffers(window);
		//remove all unhandled events from the events queue
		glfwPollEvents();
	}

	/*
		glfw allocated some memory to create the window.
		Typically this would be automatically freed at the end of the program,
		however this might become a smaller part of a larger program, meaning we need to be explicit
		about freeing the resources.
		Plus, it's a good habit to get into.
	*/
	glfwTerminate();
	return 0;
}