#include "world.h"

World::World(ComponentRegistry& componentRegistry):
	componentRegistry(componentRegistry) {}

void World::update(float frametime) {

	for (size_t i = 0; i < componentRegistry.velocities.entities.size(); ++i) {

		uint32_t id = componentRegistry.velocities.entities[i];
		VelocityComponent& velocity = componentRegistry.velocities.components[i];
		TransformComponent& transform = componentRegistry.transforms.get_component(i);

		transform.eulers += frametime / 1000.0f * velocity.angular;
	}
}