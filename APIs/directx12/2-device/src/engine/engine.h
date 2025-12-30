#pragma once
#include <windows.h>
#include <directx/d3dx12.h>
#include <d3d12.h>
#include <dxgi1_6.h>

//Windows Runtime Library, For com pointers
#include <wrl.h>
using namespace Microsoft::WRL;

class Engine {

private:

	HWND window;

	// https://learn.microsoft.com/en-us/windows/win32/api/dxgi/nn-dxgi-idxgiadapter1
	// Interestingly, objects can be converted quite easily between interfaces.
	// ComPtr: https://learn.microsoft.com/en-us/windows/win32/LearnWin32/com-coding-practices
	ComPtr<IDXGIAdapter4> adapter;

	ComPtr<ID3D12Device> device;

public:

	HRESULT create_resouces(HWND window);

	void destroy_resources();
};