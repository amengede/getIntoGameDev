#include <windows.h>

struct State {
	UINT color = COLOR_WINDOW;
	bool frameA = true;
};


LRESULT CALLBACK callback(HWND window, UINT message, WPARAM wide_parameters, LPARAM long_parameters) {

	State* myState;

	if (message == WM_CREATE) {
		CREATESTRUCT* creationInfo = reinterpret_cast<CREATESTRUCT*>(long_parameters);
		myState = reinterpret_cast<State*>(creationInfo->lpCreateParams);
		SetWindowLongPtr(window, GWLP_USERDATA, (LONG_PTR)myState);
	}
	else {
		LONG_PTR ptr = GetWindowLongPtr(window, GWLP_USERDATA);
		myState = reinterpret_cast<State*>(ptr);
	}

	switch (message) {
	case (WM_DESTROY):
		PostQuitMessage(0);
		return 0;
	case (WM_PAINT):
	{
		PAINTSTRUCT paintEvent;
		HDC deviceContext = BeginPaint(window, &paintEvent);
		FillRect(deviceContext, &(paintEvent.rcPaint), (HBRUSH)(myState->color + 1));
		EndPaint(window, &paintEvent);

		myState->frameA = !myState->frameA;
		if (myState->frameA) {
			myState->color = COLOR_WINDOW;
		}
		else {
			myState->color = COLOR_GRAYTEXT;
		}
	}
		return 0;
	default:
		return DefWindowProc(window, message, wide_parameters, long_parameters);
	}
}

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE previousInstance, PWSTR argv, int appearance) {

	const wchar_t className[] = L"myWindowClass";
	WNDCLASS windowClass = {};
	windowClass.lpfnWndProc = callback;
	windowClass.hInstance = instance;
	windowClass.lpszClassName = className;
	RegisterClass(&windowClass);

	State myState;

	HWND window = CreateWindowEx(
		0, className, L"My window", WS_OVERLAPPEDWINDOW, 
		CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT, 
		NULL, NULL, instance, &myState);
	if (window == NULL) {
		return 0;
	}
	ShowWindow(window, appearance);
	MSG message = {};
	while (GetMessage(&message, NULL, 0, 0) > 0) {
		TranslateMessage(&message);
		DispatchMessage(&message);
	}

	return 0;
}