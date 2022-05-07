#include "config.h"
#include "control/game_app.h"

int main() {

	int width = 800;
	int height = 600;
	
	GameAppCreateInfo appInfo;
	appInfo.width = width;
	appInfo.height = height;
	GameApp* app = new GameApp(&appInfo);
	
	returnCode nextAction = returnCode::CONTINUE;
	while (nextAction == returnCode::CONTINUE) {
		nextAction = app->mainLoop();
	}

	delete app;

	return 0;
}