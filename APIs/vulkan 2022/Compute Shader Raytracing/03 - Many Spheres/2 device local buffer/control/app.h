#pragma once
#include "../config.h"
#include "../view/engine.h"
#include "../model/scene.h"

class App {

private:
	Engine* graphicsEngine;
	GLFWwindow* window;
	Scene* scene;

	double lastTime, currentTime;
	int numFrames;
	float frameTime;

	void setup_glfw(int width, int height);

	void setup_timer();

	void calculate_framerate();

public:
	App(int width, int height, bool debug);
	~App();
	void run();
};