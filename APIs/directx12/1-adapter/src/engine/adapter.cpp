#include "adapter.h"
#include "logger.h"
#include <cstdint>

HRESULT get_adapter(ComPtr<IDXGIAdapter1>& chosenAdapter) {

    Logger* logger = Logger::get_logger();

    /*
    *   https://learn.microsoft.com/en-us/windows/win32/api/dxgi1_3/nf-dxgi1_3-createdxgifactory2
    *   createFactory2 variant lets us set the debug flag.
    *   factory1 can enumerate adapters
    *   dxgi1_6.h has adapter_flag3
    *   
    */
    ComPtr<IDXGIFactory1> dxgiFactory;
    uint32_t factoryCreationFlags = 0;

#if defined(_DEBUG)
    factoryCreationFlags = DXGI_CREATE_FACTORY_DEBUG;
#endif

    /*
    *   from https://learn.microsoft.com/en-us/windows/win32/api/dxgi1_3/nf-dxgi1_3-createdxgifactory2
    *
    * HRESULT CreateDXGIFactory2(
    *    UINT   Flags,
    *    REFIID riid,
    *    [out] void   **ppFactory);
    */
    /*
        IID_PPV_ARGS is a COM macro, it gets the Interface ID pointer.
        It's used to provide the globally unique id of the object being constructed.
        https://learn.microsoft.com/en-us/windows/win32/LearnWin32/com-coding-practices
    */
    if (FAILED(CreateDXGIFactory2(factoryCreationFlags, IID_PPV_ARGS(&dxgiFactory)))) {
        logger->print(L"Failed to create DXGI factory!\n");
        return (HRESULT)1L;
    }

    ComPtr<IDXGIAdapter1> adapter;

    SIZE_T maxDedicatedVideoMemory = 0;

    // Search through all available adapters
    for (UINT i = 0; dxgiFactory->EnumAdapters1(i, &adapter) != DXGI_ERROR_NOT_FOUND; ++i) {
        DXGI_ADAPTER_DESC1 adapterDescription;
        adapter->GetDesc1(&adapterDescription);

        logger->print(adapterDescription);

        bool hardware_renderer = adapterDescription.Flags & DXGI_ADAPTER_FLAG3_SOFTWARE == 0;
        
        /*
        * from https://learn.microsoft.com/en-us/windows/win32/api/d3d12/nf-d3d12-d3d12createdevice
        * HRESULT D3D12CreateDevice(
        *   [in, optional]  IUnknown          *pAdapter,
        *   D3D_FEATURE_LEVEL MinimumFeatureLevel,
        *   [in]            REFIID            riid,
        *   [out, optional] void              **ppDevice); <- NULL here indicates just to test,
        *                                                   not to actually create
        * 
        */
        bool supportsDirectX12 = SUCCEEDED(D3D12CreateDevice(
            adapter.Get(), D3D_FEATURE_LEVEL_12_0, __uuidof(ID3D12Device), nullptr));

        bool biggestSoFar = adapterDescription.DedicatedVideoMemory > maxDedicatedVideoMemory;

        if (hardware_renderer && supportsDirectX12 && biggestSoFar) {
            chosenAdapter = adapter;
            maxDedicatedVideoMemory = adapterDescription.DedicatedVideoMemory;
        }
    }

    return S_OK;
}