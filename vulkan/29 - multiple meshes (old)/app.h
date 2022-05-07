#pragma once
#include "vk_engine.h"

class App {
public:

	bool _isInitialized{ false };

	VulkanEngine* graphicsEngine;

	Scene* scene;

	void init();

	void run();

	void cleanup();
};