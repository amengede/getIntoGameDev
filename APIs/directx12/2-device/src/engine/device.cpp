#include "device.h"
#include "logger.h"

HRESULT make_device(ComPtr<IDXGIAdapter4> adapter, ComPtr<ID3D12Device>& device) {

    HRESULT result = D3D12CreateDevice(adapter.Get(), D3D_FEATURE_LEVEL_12_0, IID_PPV_ARGS(&device));

    Logger* logger = Logger::get_logger();

    if (logger->is_enabled()) {
        ComPtr<ID3D12InfoQueue> infoQueue;
        if (SUCCEEDED(device.As(&infoQueue))) {
            infoQueue->SetBreakOnSeverity(D3D12_MESSAGE_SEVERITY_CORRUPTION, TRUE);
            infoQueue->SetBreakOnSeverity(D3D12_MESSAGE_SEVERITY_ERROR, TRUE);
            infoQueue->SetBreakOnSeverity(D3D12_MESSAGE_SEVERITY_WARNING, TRUE);
        
            // Suppress messages based on their severity level
            D3D12_MESSAGE_SEVERITY severities[] =
            {
                D3D12_MESSAGE_SEVERITY_INFO
            };

            // Suppress individual messages by their ID
            D3D12_MESSAGE_ID denyIds[] = {
                D3D12_MESSAGE_ID_CLEARRENDERTARGETVIEW_MISMATCHINGCLEARVALUE,
                D3D12_MESSAGE_ID_MAP_INVALID_NULLRANGE,
                D3D12_MESSAGE_ID_UNMAP_INVALID_NULLRANGE,
            };

            D3D12_INFO_QUEUE_FILTER newFilter = {};
            newFilter.DenyList.NumSeverities = _countof(severities);
            newFilter.DenyList.pSeverityList = severities;
            newFilter.DenyList.NumIDs = _countof(denyIds);
            newFilter.DenyList.pIDList = denyIds;

            infoQueue->PushStorageFilter(&newFilter);
        }
    }

    if (FAILED(result)) {
        logger->print(L"Failed to create device!\n");
    }
    else {
        logger->print(L"Created D3D12 device!\n");
    }

    return result;

}