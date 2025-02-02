#include "config.h"
#include "control/game_app.h"

int main() {
	GameAppCreateInfo appInfo;
	appInfo.width = 800;
	appInfo.height = 600;
	GameApp* myApp = new GameApp(&appInfo);
	delete myApp;
	return 0;
}