#pragma once
#include <windows.h>
#include <dxgi.h>

//Windows Runtime Library, For com pointers
#include <wrl.h>
using namespace Microsoft::WRL;

class Engine {

private:

	HWND window;

	// https://learn.microsoft.com/en-us/windows/win32/api/dxgi/nn-dxgi-idxgiadapter1
	// Interestingly, objects can be converted quite easily between interfaces.
	// ComPtr: https://learn.microsoft.com/en-us/windows/win32/LearnWin32/com-coding-practices
	ComPtr<IDXGIAdapter1> adapter;

public:

	HRESULT create_resouces(HWND window);

	void destroy_resources();
};