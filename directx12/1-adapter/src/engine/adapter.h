#pragma once
#include <dxgi.h>
#include <dxgi1_6.h>
#include <directx/d3dx12.h>

#include <wrl.h>
using namespace Microsoft::WRL;

HRESULT get_adapter(ComPtr<IDXGIAdapter1>& chosenAdapter);