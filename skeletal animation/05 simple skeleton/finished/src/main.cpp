#include "config.h"
#include "controller/app.h"

#include "factories/factory.h"

/*
	Skeletal Animation. Stage 5: Simple Skeleton

	A skeletal animation is a hierarchy of bones, each bone acts as a "pin"
	or point of influence. It stores position and rotation info,
	and a transformation matrix.

	In addition, bones can be animated by changing their properties over time.

	The goals are:

		systems>pin_system.cpp>click_callback: Respond to mouse clicks

		systems>pin_system.cpp>update: Give the pin a local transformation

		systems>render_system.cpp>update: Bring it all together, make the cube spin around the pin.
*/

int main() {

	App* app = new App();
	Factory* factory = new Factory(
		app->renderComponents, 
		app->transformComponents,
		app->skeletons,
		app->animationSet,
		app->animations);

	factory->make_legs({ 0.0f, 0.0f, -5.0f }, { 0.0f, 0.0f, 0.0f });

	app->set_up_opengl();
	app->make_systems();

	app->run();

	delete app;
	return 0;
}