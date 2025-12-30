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
		if (FAILED(myState->create_resouces(window))) {
			return -1;
		}
	}
	else
	{
		LONG_PTR ptr = GetWindowLongPtr(window, GWLP_USERDATA);
		myState = reinterpret_cast<Engine*>(ptr);
	}

	switch (message) {

	case WM_DESTROY:
		myState->destroy_resources();
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
