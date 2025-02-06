# Direct-X 12: Adapter Selection
[Video](https://youtu.be/x_zpsz4vxWs)

In this tutorial we will take the first step to making a d3d12 renderer, by selecting the Graphics Adapter (physical device) with which to render. This tutorial follows on from the windows programming tutorials.

## Project Structure
We'll start with a very simple folder structure.

```
├── src
│   ├── engine
│   ├── main.cpp
```

The main source file will be a copy from the windows tutorials, it will create a window and hook it up the a callback function to handle events. Here's the basic idea:

<main.cpp>:
```
#include <windows.h>
#include "engine/engine.h"

LRESULT CALLBACK window_proc(HWND window, UINT message,
	WPARAM wideParameters,
	LPARAM longParameters) {

	Engine* myState;
	if (message == WM_CREATE)
	{
		CREATESTRUCT* pCreate = reinterpret_cast<CREATESTRUCT*>(longParameters);
		myState = reinterpret_cast<Engine*>(pCreate->lpCreateParams);
		SetWindowLongPtr(window, GWLP_USERDATA, (LONG_PTR)myState);
		// Initialize engine
	}
	else
	{
		LONG_PTR ptr = GetWindowLongPtr(window, GWLP_USERDATA);
		myState = reinterpret_cast<Engine*>(ptr);
	}

	switch (message) {

	case WM_DESTROY:
		// Tell engine to destroy its resources
		PostQuitMessage(0);
		return 0;

	default:
		return DefWindowProc(window, message, wideParameters, longParameters);
	}
}

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE previousInstance, PWSTR argv, int appearance) {

	// Register the window class
	const wchar_t className[] = L"Sample window class";
	WNDCLASS windowClass = {};
	windowClass.lpfnWndProc = window_proc;
	windowClass.hInstance = instance;
	windowClass.lpszClassName = className;
	RegisterClass(&windowClass);

	Engine* myState = new Engine();

	// Create the window
	HWND window = CreateWindowEx(
		0,															// optional window styles
		className,													// window class
		L"My first window",											// title
		WS_OVERLAPPEDWINDOW,										// style
		CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT,	// rect: x, y, w, h
		NULL,														// parent
		NULL,														// menu
		instance,													// instance
		myState														// additional data
	);
	if (window == NULL) {
		return 0;
	}

	ShowWindow(window, appearance);

	MSG message = {};
	while (GetMessage(&message, NULL, 0, 0) > 0) {

		TranslateMessage(&message);
		DispatchMessage(&message);
	}
}
```

We'll revisit those comments once the engine's public interface is declared, but they'll be very simple function calls when the time comes.

Let's dig a little deeper into the engine! Currently we'll need:

- an engine class
- helper functions to select an adapter
- logging code wouldn't hurt

This is what the contents of the folder will look like:
```
├── engine
│   ├── adapter.cpp/h
│   ├── engine.cpp/h
│   ├── logger.cpp/h
```

## Engine
As noted in the main file, our engine will need functions to create and destroy resources. It should also have some resources to create and destroy! Not much yet, just a handle to the window and an adapter. Here's what our header will look like:

<engine/engine.h>:
```
#pragma once
#include <windows.h>
#include <dxgi.h>

#include <wrl.h>
using namespace Microsoft::WRL;

class Engine {

private:

	HWND window;

	ComPtr<IDXGIAdapter1> adapter;

public:

	HRESULT create_resouces(HWND window);

	void destroy_resources();
};
```
dxgi is the Direct-X Graphics Infrastructure, we can think of it as low level support code for Direct-X objects (not tied to any particular version). When we call Direct-X code, it is translated to a DXGI call and then passed along to the driver. Here we need it to use the IDXGIAdapter1 component.

IDXGIAdapter1 stands for "Interface to a DXGI Adapter (version 1)" Direct-X achieves polymorphism by composition of objects. The concept is a little something like this:
```
struct Aspect1 {
    // State necessary for some use case
}

struct Aspect2 {
    // State necessary for some other use case
}

struct BaseObject {
    Aspect1 myAspect1;
    Aspect2 myAspect2;

    Aspect1& asAspect1() {
        return Aspect1;
    }
    // ...
}
```

In this way objects can be partitioned by their use cases, or additional features can be added to the same object in future revisions while keeping a (somewhat) unified codebase. [Browsing through the adapter documentation](https://learn.microsoft.com/en-us/windows/win32/api/dxgi/nn-dxgi-idxgiadapter) shows this appears to be the case. We can construct an adapter object, but cast it to various versions on the fly in order to work with different adapter features.

Having defined the public interface, we can now complete the main file.

<main.cpp>:
```
// Initialize engine
if (FAILED(myState->create_resouces(window))) {
	return -1;
}

// ...

// Tell engine to destroy its resources
myState->destroy_resources();
```

## Adapter
The public interface for the adapter is quite simple, just a single function to get the adapter.

<engine/adapter.h>:
```
#pragma once
#include <dxgi.h>
#include <dxgi1_6.h>
#include <directx/d3dx12.h>

#include <wrl.h>
using namespace Microsoft::WRL;

HRESULT get_adapter(ComPtr<IDXGIAdapter1>& chosenAdapter);
```

Interestingly we're using [DXGI version 1.6](https://learn.microsoft.com/en-us/windows/win32/api/dxgi1_6/), this is because interface version 1.6 adds the ability to enumerate graphics adapters. You may be gettting the idea that Direct-X 12 documentation is hard to read. No graphics API is perfect, but perhaps the most interesting observation is that they all seem to be imperfect in different, preventable ways. Anyway, with that function declared we can flesh out our engine.

<engine/engine.cpp>:
```
#include "engine.h"
#include "adapter.h"

HRESULT Engine::create_resouces(HWND window) {

	this->window = window;

	HRESULT result = get_adapter(adapter);

	return result;
}

void Engine::destroy_resources() {
}
```

Back to the Adapter selection,

<engine/adapter.cpp>:
```
#include "adapter.h"
#include <cstdint>

HRESULT get_adapter(ComPtr<IDXGIAdapter1>& chosenAdapter) {

    // Create a DXGI factory to enumerate physical adapters

    // Temporary object for inspection/comparison
    ComPtr<IDXGIAdapter1> adapter;

    SIZE_T maxDedicatedVideoMemory = 0;

    // Search through all available adapters, choose adapter which:
    //  1. uses hardware rendering
    //  2. supports d3d12
    //  3. has the greatest amount of VRAM

    return S_OK;
}
```

Creating the DXGI factory is fairly straightforward, we just we the debug flag if necessary and then attempt to create.
```
// Create a DXGI factory to enumerate physical adapters
ComPtr<IDXGIFactory1> dxgiFactory;
uint32_t factoryCreationFlags = 0;

#if defined(_DEBUG)
factoryCreationFlags = DXGI_CREATE_FACTORY_DEBUG;
#endif

if (FAILED(CreateDXGIFactory2(factoryCreationFlags, IID_PPV_ARGS(&dxgiFactory)))) {
    return (HRESULT)1L;
}
```
The IID_PPV_ARGS macro fetched the globally unique ID of the object to be populated. This is just a requirement of win32.

Searching for adapters is more involved. Let's enumerate first.
```
// Search through all available adapters
for (UINT i = 0; dxgiFactory->EnumAdapters1(i, &adapter) != DXGI_ERROR_NOT_FOUND; ++i) {

    // Get description of adapter
    DXGI_ADAPTER_DESC1 adapterDescription;
    adapter->GetDesc1(&adapterDescription);

    // choose adapter which:
    //  1. uses hardware rendering
    //  2. supports d3d12
    //  3. has the greatest amount of VRAM
}
```

Before we proceed further with this, it might help to inspect the adapter descriptions.

<engine/logger.h>:
```
#pragma once
#include <string>
#include <dxgi.h>
#include <dxgi1_6.h>
#include <directx/d3dx12.h>

class Logger {
public:

    static Logger* logger;

    static Logger* get_logger();

    void set_mode(bool mode);

    bool is_enabled();

    void print(DXGI_ADAPTER_DESC1 adapterDescription);

private:

    bool enabled;
};
```
This is an adaption of the logger I use in my Vulkan tutorials! The Adapter Description struct has the following fields:

```
typedef struct DXGI_ADAPTER_DESC1 {
  WCHAR  Description[128];
  UINT   VendorId;
  UINT   DeviceId;
  UINT   SubSysId;
  UINT   Revision;
  SIZE_T DedicatedVideoMemory;
  SIZE_T DedicatedSystemMemory;
  SIZE_T SharedSystemMemory;
  LUID   AdapterLuid;
  UINT   Flags;
} DXGI_ADAPTER_DESC1;
```

We can print some of these to the terminal, specifically name and dedicated memory amount.

<engine/logger.cpp>
```
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

void Logger::print(DXGI_ADAPTER_DESC1 adapterDescription) {

	if (!enabled) {
		return;
	}

	std::wstringstream builder;
	OutputDebugString(L"----");
	OutputDebugString(adapterDescription.Description);
	OutputDebugString(L"----\n");
	builder << "Dedicated VRAM: " << adapterDescription.DedicatedVideoMemory << std::endl;
	OutputDebugString(builder.str().c_str());
}
```

I won't go further into debug logging in this tutorial, however it's all coded up in the source code. Suffice to say, this shows how we can read the properties of an adapter description.

Hardware rendering can be verified by checking the flags.

<engine/adapter.cpp>:
```
// choose adapter which:
//  1. uses hardware rendering
bool hardware_renderer = adapterDescription.Flags & DXGI_ADAPTER_FLAG3_SOFTWARE == 0;
```

d3d12 support can be queried by checking whether the adapter can create a device. Interestingly, if we pass in a null pointer for the device to populate, DXGI understands that rather than creating a device, we're checking to see whether that function would have been supported.

```
// choose adapter which:
//  2. supports d3d12
bool supportsDirectX12 = SUCCEEDED(D3D12CreateDevice(
    adapter.Get(), D3D_FEATURE_LEVEL_12_0, __uuidof(ID3D12Device), nullptr));
```

VRAM comparison is also simple, just a case of reading the dedicatedVideoMemory field.

```
// choose adapter which:
//  3. has the greatest amount of VRAM
bool biggestSoFar = adapterDescription.DedicatedVideoMemory > maxDedicatedVideoMemory;
```

Then as we look through the adapters, whenever we find a more suitable one we update our choice.
```
// Search through all available adapters
for (UINT i = 0; dxgiFactory->EnumAdapters1(i, &adapter) != DXGI_ERROR_NOT_FOUND; ++i) {

    // Get description of adapter
    DXGI_ADAPTER_DESC1 adapterDescription;
    adapter->GetDesc1(&adapterDescription);

    // choose adapter which:
    //  1. uses hardware rendering
    ...
    //  2. supports d3d12
    ...
    //  3. has the greatest amount of VRAM
    ...

    if (hardware_renderer && supportsDirectX12 && biggestSoFar) {
        chosenAdapter = adapter;
        maxDedicatedVideoMemory = adapterDescription.DedicatedVideoMemory;
    }
}
```

And that's it! As an extension, try adding in logging functions to print some status messages out to the terminal (or check the provided code).