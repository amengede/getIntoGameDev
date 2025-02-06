# Direct-X 12: Device Creation

In the previous tutorial we started learning about DirectX 12 and selected an appropriate graphics adapter. In this tutorial we will create a Direct3D 12 device.

## What is a device?
One of the coolest things about modern graphics APIs is they converge around a number of similar abstractions. Adapters and Devices serve the same purpose as Vulkan's Physical and Logical Devices. That is, the adapter is a record of a physical device, whereas a device is an interface to that physical device. D3D12 devices are used to create GPU resources such as command lists, resources and resource views.

## Public interface
Let's add a new header and source file to help with device creation.

```
├── engine
│   ├── adapter.cpp/h
│   ├── engine.cpp/h
│   ├── device.cpp/h
│   ├── logger.cpp/h
```

The header will just contain a single function, used to create the device.

<engine/device.h>:
```
#pragma once
#include <Windows.h>
#include <directx/d3dx12.h>
#include <d3d12.h>
#include <dxgi1_6.h>

#include <wrl.h>
using namespace Microsoft::WRL;

HRESULT make_device(ComPtr<IDXGIAdapter4> adapter, ComPtr<ID3D12Device2>& device);
```

Here the DirectX 12 extension header is being included in order to have access to some additional definitions used in device creation. Let's now give the engine a device.

<engine/engine.h>
```
class Engine {

private:

	HWND window;

	ComPtr<IDXGIAdapter4> adapter;

	ComPtr<ID3D12Device> device;

public:

	// ...
};
```
In the engine initialization, we'll use the function to populate the device.

<engine/engine.cpp>
```
#include "engine.h"
#include "adapter.h"
#include "logger.h"
#include "device.h"

HRESULT Engine::create_resouces(HWND window) {

	this->window = window;

	Logger* logger = Logger::get_logger();

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
```

Before we go and implement the device creation function, however, there's one thing we need to do with the engine. I want to enable debug messages, similar to validation layers. In order to do this, debug messages must first be explicitly enabled.

```
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
	// ...
}
```

## Implementation
Now let's implement the function to create the device!

<engine/device.cpp>:
```
#include "device.h"
#include "logger.h"

HRESULT make_device(ComPtr<IDXGIAdapter4> adapter, ComPtr<ID3D12Device>& device) {

    // Create the Device
    HRESULT result = D3D12CreateDevice(adapter.Get(), D3D_FEATURE_LEVEL_12_0, IID_PPV_ARGS(&device));

    Logger* logger = Logger::get_logger();

    if (logger->is_enabled()) {
        // Control which device debug messages to show.
    }

    if (FAILED(result)) {
        logger->print(L"Failed to create device!\n");
    }
    else {
        logger->print(L"Created D3D12 device!\n");
    }

    return result;

}
```

The device creation is one of the easiest parts of this tutorial, we more or less fetch an abstration of the adapter.

By default, since we enabled the debug layer, all of its output will be logged. For practical purposes however this may be too much. Direct-X 12 lets us add filters to the device's info queue in order to block certain types of messages. Let's look at how to do that.

```
if (logger->is_enabled()) {
    // Fetch device's info queue
    // Specify severity levels to break on
    // Specify which severity levels to ignore
    // Specify which message IDs to ignore
}
```

The info queue is an interface of the device, so the device can be "cast" to an info queue.

```
if (logger->is_enabled()) {
    ComPtr<ID3D12InfoQueue> infoQueue;
    if (SUCCEEDED(device.As(&infoQueue))) {
        // Specify severity levels to break on
        // Specify which severity levels to ignore
        // Specify which message IDs to ignore
    }
}
```
Break Levels can be directly specified by the info queue's methods.
```
if (logger->is_enabled()) {
    ComPtr<ID3D12InfoQueue> infoQueue;
    if (SUCCEEDED(device.As(&infoQueue))) {
        
        // Specify severity levels to break on
        infoQueue->SetBreakOnSeverity(D3D12_MESSAGE_SEVERITY_CORRUPTION, TRUE);
        infoQueue->SetBreakOnSeverity(D3D12_MESSAGE_SEVERITY_ERROR, TRUE);
        infoQueue->SetBreakOnSeverity(D3D12_MESSAGE_SEVERITY_WARNING, TRUE);
    
        // Specify which severity levels to ignore
        // Specify which message IDs to ignore
    }
}
```
Message ignoring is done via a filter object. Filters are structs which are configured seperately before being linked to the message queue.

```
if (logger->is_enabled()) {
    ComPtr<ID3D12InfoQueue> infoQueue;
    if (SUCCEEDED(device.As(&infoQueue))) {

        // Specify severity levels to break on
        infoQueue->SetBreakOnSeverity(D3D12_MESSAGE_SEVERITY_CORRUPTION, TRUE);
        infoQueue->SetBreakOnSeverity(D3D12_MESSAGE_SEVERITY_ERROR, TRUE);
        infoQueue->SetBreakOnSeverity(D3D12_MESSAGE_SEVERITY_WARNING, TRUE);

        D3D12_INFO_QUEUE_FILTER newFilter = {};
    
        // Specify which severity levels to ignore
        D3D12_MESSAGE_SEVERITY severities[] =
        {
            D3D12_MESSAGE_SEVERITY_INFO
        };
        newFilter.DenyList.NumSeverities = _countof(severities);
        newFilter.DenyList.pSeverityList = severities;

        // Specify which message IDs to ignore

        infoQueue->PushStorageFilter(&newFilter);
    }
}
```

Both severity and ID blocks can be specified in the one filter.
```
if (logger->is_enabled()) {
    ComPtr<ID3D12InfoQueue> infoQueue;
    if (SUCCEEDED(device.As(&infoQueue))) {

        // Specify severity levels to break on
        infoQueue->SetBreakOnSeverity(D3D12_MESSAGE_SEVERITY_CORRUPTION, TRUE);
        infoQueue->SetBreakOnSeverity(D3D12_MESSAGE_SEVERITY_ERROR, TRUE);
        infoQueue->SetBreakOnSeverity(D3D12_MESSAGE_SEVERITY_WARNING, TRUE);

        D3D12_INFO_QUEUE_FILTER newFilter = {};
    
        // Specify which severity levels to ignore
        D3D12_MESSAGE_SEVERITY severities[] =
        {
            D3D12_MESSAGE_SEVERITY_INFO
        };
        newFilter.DenyList.NumSeverities = _countof(severities);
        newFilter.DenyList.pSeverityList = severities;

        // Specify which message IDs to ignore
        D3D12_MESSAGE_ID denyIds[] = {
            D3D12_MESSAGE_ID_CLEARRENDERTARGETVIEW_MISMATCHINGCLEARVALUE,
            D3D12_MESSAGE_ID_MAP_INVALID_NULLRANGE,
            D3D12_MESSAGE_ID_UNMAP_INVALID_NULLRANGE,
        };
        newFilter.DenyList.NumIDs = _countof(denyIds);
        newFilter.DenyList.pIDList = denyIds;

        infoQueue->PushStorageFilter(&newFilter);
    }
}
```
And there we have it! If we did everything correctly we should now see that our device has been successfully created.