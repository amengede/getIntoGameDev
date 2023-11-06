#pragma once
#include "../config.h"
#include "../backend/buffer.h"
#include "../components/sphere_component.h"
#include "../components/component_set.h"

class RenderSystem {
public:

    RenderSystem(std::vector<unsigned int>& shaders, 
        GLFWwindow* window,
        unsigned int colorbuffer);
    ~RenderSystem();
    
    void update();
    
private:

    std::vector<unsigned int>& shaders;

    unsigned int VAO, colorbuffer;
    int workgroup_count_x, workgroup_count_y;

};