#pragma once
#include "../config.h"
#include <GLFW/glfw3.h>
#include "../components/registry.h"

class RenderSystem {
public:

    RenderSystem(uint32_t shader, GLFWwindow* window, ComponentRegistry& componentRegistry);
    
    void update();
    
private:

    uint32_t shader;
    GLFWwindow* window;
    ComponentRegistry& componentRegistry;
    uint32_t colorLocation;
};