#pragma once
#include "../config.h"
#include "../components/camera_component.h"
#include "../components/component_set.h"

class CameraSystem {
public:

    CameraSystem(std::vector<unsigned int>& shaders, GLFWwindow* window, 
        ComponentSet<CameraComponent>& cameras);
    
    bool update(float dt);
    
private:
    std::vector<unsigned int>& shaders;
    unsigned int forwardsLocation, rightLocation;
    unsigned int upLocation, posLocation;
    const glm::vec3 global_up = {0.0f, 0.0f, 1.0f};
    GLFWwindow* window;
    float dx, dy;

    ComponentSet<CameraComponent>& cameras;
};