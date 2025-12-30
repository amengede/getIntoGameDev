#pragma once
#include "../view/engine.h"
#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h>

struct GameAppCreateInfo {
	int width;
	int height;
};

enum class returnCode {
	CONTINUE, QUIT
};

class GameApp {
public:
	GameApp(GameAppCreateInfo* createInfo);
	returnCode mainLoop();
	~GameApp();
private:
	GLFWwindow* makeWindow();
	returnCode processInput();
	void calculateFrameRate();

	GLFWwindow* window;
	int width, height;
	Engine* renderer;

	double lastTime, currentTime;
	int numFrames;
	float frameTime;
};
