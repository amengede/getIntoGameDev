#include "factory.h"

Factory::Factory(
    ComponentSet<PhysicsComponent>& physicsComponents,
    ComponentSet<RenderComponent>& renderComponents,
    ComponentSet<TransformComponent>& transformComponents):
physicsComponents(physicsComponents),
renderComponents(renderComponents),
transformComponents(transformComponents) {
}

unsigned int Factory::allocate_id() {
        
	if (garbage_bin.size() > 0) {
		uint32_t id = garbage_bin[garbage_bin.size() - 1];
		garbage_bin.pop_back();
		return id;
	}
	else {
		return entities_made++;
	}
}

void Factory::make_cube(glm::vec3 position, glm::vec3 eulers, 
    glm::vec3 eulerVelocity) {

	unsigned int id = allocate_id();

	TransformComponent transform;
	transform.position = position;
	transform.eulers = eulers;
	transformComponents.insert(id, transform);

	PhysicsComponent physics;
	physics.velocity = {0.0f, 0.0f, 0.0f};
	physics.eulerVelocity = eulerVelocity;
	physicsComponents.insert(id, physics);
	
	RenderComponent render;
	render.objectType = ObjectType::eBox;
	renderComponents.insert(id, render);
}