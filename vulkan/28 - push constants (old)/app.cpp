#pragma once
#include "app.h"
#include <GLFW/glfw3.h>

void App::init() {
	graphicsEngine = new VulkanEngine;
	scene = new Scene;
	graphicsEngine->run();
	_isInitialized = true;
}

void App::run() {

	if (!_isInitialized) {
		return;
	}

	while (!glfwWindowShouldClose(graphicsEngine->window)) {
		glfwPollEvents();
		graphicsEngine->drawFrame(scene);
	}
	vkDeviceWaitIdle(graphicsEngine->device);
}

void App::cleanup() {
	if (_isInitialized) {
		graphicsEngine->cleanup();
		delete graphicsEngine;
		delete scene;
	}
}