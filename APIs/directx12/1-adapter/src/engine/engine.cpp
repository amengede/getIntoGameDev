#include "engine.h"
#include "adapter.h"
#include "logger.h"

HRESULT Engine::create_resouces(HWND window) {

	this->window = window;

	Logger* logger = Logger::get_logger();
	logger->set_mode(true);

	HRESULT result = get_adapter(adapter);

	return result;
}

void Engine::destroy_resources() {
	Logger* logger = Logger::get_logger();
	logger->print(L"Goodbye see you!\n");
}