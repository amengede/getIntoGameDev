#include "game_app.h"

GameApp::GameApp(GameAppCreateInfo* createInfo) {
	this->width = createInfo->width;
	this->height = createInfo->height;

	lastTime = glfwGetTime();
	numFrames = 0;
	frameTime = 16.0f;

	window = makeWindow();

	renderer = new Engine(width, height);
}

GLFWwindow* GameApp::makeWindow() {
	glfwInit();

	glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
	glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 5);
	glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

	GLFWwindow* window = glfwCreateWindow(640, 480, "This is working I hope", NULL, NULL);

	glfwMakeContextCurrent(window);

	if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
		std::cout << "GLAD initialization failed\n";
		return NULL;
	}

	glViewport(0, 0, width, height);

	return window;
}

returnCode GameApp::processInput() {

	if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS) {
		return returnCode::QUIT;
	}
	return returnCode::CONTINUE;
}

returnCode GameApp::mainLoop() {

	returnCode nextAction{ processInput() };
	glfwPollEvents();

	if (glfwWindowShouldClose(window)) {
		nextAction = returnCode::QUIT;
	}

	//draw
	renderer->render();
	glfwSwapBuffers(window);

	calculateFrameRate();

	return nextAction;
}

GameApp::~GameApp() {
	//free memory
	delete renderer;
	glfwTerminate();
}

void GameApp::calculateFrameRate() {
	currentTime = glfwGetTime();
	double delta = currentTime - lastTime;

	if (delta >= 1) {
		int framerate{ std::max(1, int(numFrames / delta)) };
		std::stringstream title;
		title << "Running at " << framerate << " fps.";
		glfwSetWindowTitle(window, title.str().c_str());
		lastTime = currentTime;
		numFrames = -1;
		frameTime = float(1000.0 / framerate);
	}

	++numFrames;
}