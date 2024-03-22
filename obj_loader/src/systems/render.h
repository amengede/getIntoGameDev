#pragma once
#include "../config.h"
#include <GLFW/glfw3.h>
#include "../components/registry.h"
#include "../factories/model_factory.h"

class RenderSystem {
public:

    RenderSystem(uint32_t shader, GLFWwindow* window, ComponentRegistry& componentRegistry);
    ~RenderSystem();
    
    void update();
    
private:

    void build_models();
    glm::mat4 build_model_transform(TransformComponent& transform);

    uint32_t shader, modelLocation;
    GLFWwindow* window;
    ComponentRegistry& componentRegistry;
    std::unordered_map<ObjectType, Mesh> meshes;
};