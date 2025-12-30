#pragma once
#include <directx/d3dx12.h>
#include <d3d12.h>
#include <dxgi1_6.h>

#include <wrl.h>
using namespace Microsoft::WRL;

HRESULT get_adapter(ComPtr<IDXGIAdapter4>& chosenAdapter);