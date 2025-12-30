#include "config.h"
#include "controller/app.h"

#include "factories/factory.h"

/*
	Skeletal Animation. Stage 4: Local Transformations

	Skeletal animation is a hierarchical system of affine transformations
	(an affine transformation is simply a combination of translations and rotations.
	It can move a mesh around, but can't change its size or shape)

	In this exercise we have a cube spinning around a pin, we can
	click on the screen to set the position of the pin.

	The goals are:

		systems>pin_system.cpp>click_callback: Respond to mouse clicks

		systems>pin_system.cpp>update: Give the pin a local transformation

		systems>render_system.cpp>update: Bring it all together, make the cube spin around the pin.
	
	Note: this will look a little dodgy, the purpose is to get a transformation system up quickly,
	and so perspective projection was removed.
*/

int main() {

	App* app = new App();
	Factory* factory = new Factory(
		app->physicsComponents, app->renderComponents, 
		app->transformComponents);

	app->pin = factory->drop_pin();
	
	factory->make_cube(
		{0.0f, 0.0f, -1.0f}, {0.0f, 0.0f, 0.0f}, {0.0f, 0.0f, 0.0f});

	app->set_up_opengl();
	app->make_systems();

	app->run();

	delete app;
	return 0;
}