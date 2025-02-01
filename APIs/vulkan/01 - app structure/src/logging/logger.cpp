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