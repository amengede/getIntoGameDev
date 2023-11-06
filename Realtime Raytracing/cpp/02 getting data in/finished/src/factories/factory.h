#pragma once
#include "../config.h"
#include "../components/camera_component.h"
#include "../components/sphere_component.h"
#include "../components/component_set.h"

class Factory {

public:
    Factory(
        ComponentSet<CameraComponent>& cameraComponents, 
        ComponentSet<SphereComponent>& sphereComponents);
    
    ~Factory();

    void make_camera(glm::vec3 position, glm::vec3 eulers);
    void make_sphere();

private:

    unsigned int entities_made = 0;
    std::vector<unsigned int> garbage_bin;

    ComponentSet<CameraComponent>& cameraComponents;
    ComponentSet<SphereComponent>& sphereComponents;

    unsigned int allocate_id();

};