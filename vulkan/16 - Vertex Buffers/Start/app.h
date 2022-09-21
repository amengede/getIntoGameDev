#pragma once
#include "config.h"
#include "engine.h"

class App {

private:
	Engine* graphicsEngine;
	GLFWwindow* window;
	Scene* scene;

	double lastTime, currentTime;
	int numFrames;
	float frameTime;

	void build_glfw_window(int width, int height, bool debugMode);

	void calculateFrameRate();

public:
	App(int width, int height, bool debug);
	~App();
	void run();
};