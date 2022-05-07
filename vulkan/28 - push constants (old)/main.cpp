#include <iostream>
#include "app.h"

int main() {
	App* app = new App;

	try {
		app->init();
		app->run();
		app->cleanup();
		delete app;
	}
	catch (const std::exception& e) {
		std::cerr << e.what() << std::endl;
		return EXIT_FAILURE;
	}

	return EXIT_SUCCESS;
}