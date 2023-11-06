#pragma once
#include "../config.h"
#include "../components/camera_component.h"
#include "../components/component_set.h"

class Factory {

public:
    Factory(ComponentSet<CameraComponent>& cameraComponents);
    
    ~Factory();

    void make_camera(glm::vec3 position, glm::vec3 eulers);

private:

    unsigned int entities_made = 0;
    std::vector<unsigned int> garbage_bin;

    ComponentSet<CameraComponent>& cameraComponents;

    unsigned int allocate_id();

};