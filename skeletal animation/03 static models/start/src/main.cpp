#include "config.h"
#include "controller/app.h"

#include "factories/factory.h"

/*
	Skeletal Animation. Stage 3: Loading static models

	This ties together the previous two stages. The goal 
	is to go to factories/model_factory, and implement the
	described functions. Once that's done, a cube shall appear!
*/

int main() {

	App* app = new App();
	Factory* factory = new Factory(
		app->physicsComponents, app->renderComponents, 
		app->transformComponents);
	
	factory->make_cube(
		{0.0f, 0.0f, -5.0f}, {0.0f, 0.0f, 0.0f}, {1.0f, 2.0f, 3.0f});

	app->set_up_opengl();
	app->make_systems();

	app->run();

	delete app;
	return 0;
}