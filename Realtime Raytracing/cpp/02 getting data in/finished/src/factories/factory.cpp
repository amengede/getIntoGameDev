#include "factory.h"

Factory::Factory(
	ComponentSet<CameraComponent>& cameraComponents, 
	ComponentSet<SphereComponent>& sphereComponents):
cameraComponents(cameraComponents),
sphereComponents(sphereComponents) {
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

void Factory::make_camera(glm::vec3 position, glm::vec3 eulers) {

	unsigned int id = allocate_id();

	CameraComponent camera;
	camera.position = position;
	camera.eulers = eulers;
    cameraComponents.insert(id, camera);
}

void Factory::make_sphere() {

	unsigned int id = allocate_id();
	SphereComponent sphere;
	sphere.center = glm::vec3(
		random_float(3.0f, 10.0f), 
		random_float(-8.0f, 8.0f), 
		random_float(-8.0f, 8.0f));
	sphere.radius = random_float(0.1f, 2.0f);
	sphere.color = glm::vec3(
		random_float(0.0f, 1.0f), 
		random_float(0.0f, 1.0f), 
		random_float(0.0f, 1.0f));

    sphereComponents.insert(id, sphere);
}