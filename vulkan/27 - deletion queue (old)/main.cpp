#include <iostream>
#include "vk_engine.h"

int main() {
	VulkanEngine engine;

	try {
		engine.run();
	}
	catch (const std::exception& e) {
		std::cerr << e.what() << std::endl;
		return EXIT_FAILURE;
	}

	return EXIT_SUCCESS;
}