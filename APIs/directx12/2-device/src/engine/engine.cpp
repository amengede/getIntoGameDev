#include "engine.h"
#include "adapter.h"
#include "logger.h"
#include "device.h"

HRESULT Engine::create_resouces(HWND window) {

	this->window = window;

	Logger* logger = Logger::get_logger();

	logger->set_mode(false);

#if defined(_DEBUG)
	logger->set_mode(true);
	ComPtr<ID3D12Debug> debugInterface;
	D3D12GetDebugInterface(IID_PPV_ARGS(&debugInterface));
	debugInterface->EnableDebugLayer();
#endif

	HRESULT result = get_adapter(adapter);
	if (FAILED(result)) {
		return result;
	}

	result = make_device(adapter, device);
	if (FAILED(result)) {
		return result;
	}

	return result;
}

void Engine::destroy_resources() {
	Logger* logger = Logger::get_logger();
	logger->print(L"Goodbye see you!\n");
}