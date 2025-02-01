#include <iostream>
#include "logger.h"

Logger* Logger::logger;

void Logger::set_mode(bool mode) {
	enabled = mode;
}

bool Logger::is_enabled() {
	return enabled;
}

Logger* Logger::get_logger() {
	if (!logger) {
		logger = new Logger();
	}

	return logger;
}

void Logger::print(std::string message) {

	if (!enabled) {
		return;
	}

	std::cout << message << std::endl;
}

void Logger::report_version_number(uint32_t version) {
	
	if (!enabled) {
		return;
	}

	std::cout << "System can support vulkan Variant: " << vk::apiVersionVariant(version)
		<< ", Major: " << vk::apiVersionMajor(version)
		<< ", Minor: " << vk::apiVersionMinor(version)
		<< ", Patch: " << vk::apiVersionPatch(version) << std::endl;
}

void Logger::print_list(const char** list, uint32_t count) {

	if (!enabled) {
		return;
	}

	for (uint32_t i = 0; i < count; ++i) {
		std::cout << "\t\"" << list[i] << "\"" << std::endl;
	}
}