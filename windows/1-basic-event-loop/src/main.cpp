#include <windows.h>

/*
* @brief callback to process messages sent to a window.
* 
* @param window Handle to the calling window.
* @param message the message received.
* @param wide_parameters additional info (wide char format), depends on the message
* @param long_parameters additional info (long format), depends on the message
*/
LRESULT CALLBACK window_proc(HWND window, UINT message,
	WPARAM wide_parameters,
	LPARAM long_parameters) {
	switch (message) {

	case WM_DESTROY:
		PostQuitMessage(0);
		return 0;

	case WM_PAINT:
	{
		PAINTSTRUCT paintEvent;

		/*
		* Prepares the window for painting and populates a paintEvent with relevant info
		*
		* Returns a handle to a display device context
		*/
		HDC deviceContext = BeginPaint(window, &paintEvent);

		/*
		* uses a deviceContext to fill a rect with a color.
		* for some reason, if using a macro one must always be added to the color.
		*/
		FillRect(deviceContext, &paintEvent.rcPaint, (HBRUSH)(COLOR_WINDOW + 1));

		/*
		* presents to the window
		*/
		EndPaint(window, &paintEvent);
	}
	return 0;
	default:
		return DefWindowProc(window, message, wide_parameters, long_parameters);
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
		NULL														// additional data
	);
	if (window == NULL) {
		return 0;
	}

	ShowWindow(window, appearance);

	// message loop
	MSG message = {};
	/*
	*	BOOL GetMessage(
	*		[out] LPMSG message, 
	*		[in, optional] HWND window, 
	*		[in] UINT filterMin, 
	*		[in] UINT filterMax);
	* 
	* Takes a message, either from the calling thread's message queue,
	* or an unqueued message sent from another window.
	* 
	* message: populated by function
	* window: to receive from, NULL means any window
	* filters: can specify a specific range to poll for
	* 
	* returns: 0 on quit, nonzero otherwise. -1 indicates error
	*/
	while (GetMessage(&message, NULL, 0, 0) > 0) {

		/*
		*	BOOL TranslateMessage( [in] const MSG* message);
		* 
		* Takes a virtual message and translates it into a character message.
		* 
		* If the input is virtual, translation occurs. The resulting character message
		* is posted to the thread's message queue (to be later fetched by GetMessage),
		* and a nonzero value is returned.
		* 
		* If the input is a character message already (it happens), no translation 
		* or posting occurs and zero is returned.
		*/
		TranslateMessage(&message);

		/*
		*	LRESULT DispatchMessage([in] const MSG *message);
		* 
		* Dispatches a message to the window's window_proc callback.
		*/
		DispatchMessage(&message);
	}
}