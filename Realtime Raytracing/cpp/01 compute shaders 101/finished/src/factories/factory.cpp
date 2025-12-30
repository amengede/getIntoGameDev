#include "factory.h"

Factory::Factory(ComponentSet<CameraComponent>& cameraComponents):
cameraComponents(cameraComponents) {
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
