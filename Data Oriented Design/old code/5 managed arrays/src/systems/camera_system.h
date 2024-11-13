#pragma once
#include "../config.h"
#include "../components/camera_component.h"
#include "../components/transform_component.h"
#include "../components/component_set.h"

class CameraSystem {
public:

    CameraSystem(std::vector<unsigned int>& shaders, GLFWwindow* window);
    
    bool update(
        ComponentSet<TransformComponent> &transformComponents,
        unsigned int cameraID, CameraComponent& cameraComponent, float dt);
    
private:
    std::vector<unsigned int>& shaders;
    std::vector<unsigned int> viewLocation;
    glm::vec3 global_up = {0.0f, 0.0f, 1.0f};
    GLFWwindow* window;
};