#include "config.h"
#include "controller/app.h"

#include "components/camera_component.h"

#include "factories/factory.h"

int main() {

	App* app = new App();
	Factory* factory = new Factory(app->cameraComponents);
	
	factory->make_camera(
		{0.0f, 0.0f, 1.0f}, {0.0f, 0.0f,0.0f});

	app->set_up_opengl();
	app->make_systems();

	app->run();

	delete app;
	return 0;
}