#pragma once
#include <Windows.h>
#include <directx/d3dx12.h>
#include <d3d12.h>
#include <dxgi1_6.h>

#include <wrl.h>
using namespace Microsoft::WRL;

HRESULT make_device(ComPtr<IDXGIAdapter4> adapter, ComPtr<ID3D12Device>& device);