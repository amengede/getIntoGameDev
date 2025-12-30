#include <iostream>
#include "logger.h"
#include <debugapi.h>
#include <string.h>
#include <sstream>

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

void Logger::print(LPCWSTR message) {

	if (!enabled) {
		return;
	}

	OutputDebugString(message);
}

void Logger::print(DXGI_ADAPTER_DESC1 adapterDescription) {

	if (!enabled) {
		return;
	}

	/*
	* typedef struct DXGI_ADAPTER_DESC1
    {
    WCHAR Description[ 128 ];
    UINT VendorId;
    UINT DeviceId;
    UINT SubSysId;
    UINT Revision;
    SIZE_T DedicatedVideoMemory;
    SIZE_T DedicatedSystemMemory;
    SIZE_T SharedSystemMemory;
    LUID AdapterLuid;
    UINT Flags;
    } 	DXGI_ADAPTER_DESC1;
	*/

	std::wstringstream builder;
	OutputDebugString(L"----");
	OutputDebugString(adapterDescription.Description);
	OutputDebugString(L"----\n");
	builder << "Dedicated VRAM: " << adapterDescription.DedicatedVideoMemory << std::endl;
	OutputDebugString(builder.str().c_str());
}