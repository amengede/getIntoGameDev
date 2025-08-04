#include <windows.h>
#include <d2d1.h>

template <class T> void safe_release(T** ppT) {

    if (!*ppT) {
        return;
    }

    (*ppT)->Release();
    *ppT = NULL;
}

class MainWindow {

private:

	ID2D1HwndRenderTarget* renderTarget = NULL;
	ID2D1SolidColorBrush* brush = NULL;
	D2D1_ELLIPSE ellipse;

public:

	HWND window;
	ID2D1Factory* factory = NULL;

	HRESULT create_resouces() {

		HRESULT result = S_OK;

		if (renderTarget) {
			return result;
		}

		RECT rect;
		GetClientRect(window, &rect);

		D2D1_SIZE_U size = D2D1::SizeU(rect.right, rect.bottom);

		result = factory->CreateHwndRenderTarget(
			D2D1::RenderTargetProperties(),
			D2D1::HwndRenderTargetProperties(window, size),
			&renderTarget);

		if (FAILED(result)) {
			return result;
		}

		const D2D1_COLOR_F color = D2D1::ColorF(1.0f, 1.0f, 0);
		result = renderTarget->CreateSolidColorBrush(color, &brush);

		if (FAILED(result)) {
			return result;
		}

		calculate_layout();

		return result;
	}

	void destroy_resources() {

		safe_release(&renderTarget);
		safe_release(&brush);
	}

	void calculate_layout() {

		if (!renderTarget) {
			return;
		}

		D2D1_SIZE_F size = renderTarget->GetSize();
		const float x = size.width / 2;
		const float y = size.height / 2;
		const float radius = min(x, y);
		ellipse = D2D1::Ellipse(D2D1::Point2F(x, y), radius, radius);
	}

	void paint() {

		HRESULT result = create_resouces();
		if (FAILED(result)) {
			return;
		}

		PAINTSTRUCT paintEvent;
		BeginPaint(window, &paintEvent);

		renderTarget->BeginDraw();

		renderTarget->Clear(D2D1::ColorF(D2D1::ColorF::SkyBlue));
		renderTarget->FillEllipse(ellipse, brush);

		result = renderTarget->EndDraw();
		if (FAILED(result) || result == D2DERR_RECREATE_TARGET) {
			destroy_resources();
		}
		EndPaint(window, &paintEvent);
	}

	void resize() {
		if (!renderTarget) {
			return;
		}

		RECT rect;
		GetClientRect(window, &rect);

		D2D1_SIZE_U size = D2D1::SizeU(rect.right, rect.bottom);

		renderTarget->Resize(size);
		calculate_layout();
		InvalidateRect(window, NULL, FALSE);
	}
};

LRESULT CALLBACK window_proc(HWND window, UINT message,
	WPARAM wideParameters,
	LPARAM longParameters) {

	MainWindow* myState;
	if (message == WM_CREATE)
	{
		CREATESTRUCT* pCreate = reinterpret_cast<CREATESTRUCT*>(longParameters);
		myState = reinterpret_cast<MainWindow*>(pCreate->lpCreateParams);
		SetWindowLongPtr(window, GWLP_USERDATA, (LONG_PTR)myState);
		if (FAILED(D2D1CreateFactory(
			D2D1_FACTORY_TYPE_SINGLE_THREADED, &(myState->factory)))) {
			return -1;
		}
	}
	else
	{
		LONG_PTR ptr = GetWindowLongPtr(window, GWLP_USERDATA);
		myState = reinterpret_cast<MainWindow*>(ptr);
	}

	switch (message) {

	case WM_DESTROY:
		myState->destroy_resources();
		safe_release(&(myState->factory));
		PostQuitMessage(0);
		return 0;

	case WM_PAINT:
		myState->paint();
		return 0;

	case WM_SIZE:
		myState->resize();
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

	MainWindow* myState = new MainWindow();

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

	myState->window = window;

	ShowWindow(window, appearance);

	MSG message = {};
	while (GetMessage(&message, NULL, 0, 0) > 0) {

		TranslateMessage(&message);
		DispatchMessage(&message);
	}
}