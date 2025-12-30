#include "app.h"
#include "../backend/glfw_backend.h"

App::App() {

	constexpr int width = 800, height = 600;
	window = build_window(width, height, "ID Tech 12");
	engine = new Engine(window);
	main_loop();
}

void App::main_loop() {

	while (!glfwWindowShouldClose(window)) {
		glfwPollEvents();

		engine->draw();
	}

	delete engine;
}