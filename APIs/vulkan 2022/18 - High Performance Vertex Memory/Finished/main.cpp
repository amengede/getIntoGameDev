#include "control/app.h"

int main() {

	App* myApp = new App(640, 480, true);

	myApp->run();
	delete myApp;

	return 0;
}