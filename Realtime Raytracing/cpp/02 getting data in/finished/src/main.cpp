#include "config.h"
#include "controller/app.h"

#include "components/camera_component.h"

#include "factories/factory.h"

int main() {

	App* app = new App();
	Factory* factory = new Factory(app->cameraComponents, app->sphereComponents);
	
	factory->make_camera(
		{0.0f, 0.0f, 1.0f}, {0.0f, 0.0f,0.0f});
	
	for (int i = 0; i < 64; ++i) {
		factory->make_sphere();
	}

	app->set_up_opengl();
	app->make_systems();

	app->run();

	delete app;
	return 0;
}