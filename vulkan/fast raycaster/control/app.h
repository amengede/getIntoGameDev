#pragma once
#include "../config.h"
#include "../view/engine.h"
#include "../model/scene.h"

class App {

private:
	Engine* graphicsEngine;
	GLFWwindow* window;

	double lastTime, currentTime;
	int numFrames;
	float frameTime;

	int trialCount = 0;
	long long renderTimeNaive = 0, renderTimeBres = 0;

	void build_glfw_window(int width, int height);

	void handle_mouse();

	void handle_keys();

	void calculateFrameRate();

public:
	App(int width, int height, bool debug);
	~App();
	void run();

	Scene* scene;
};