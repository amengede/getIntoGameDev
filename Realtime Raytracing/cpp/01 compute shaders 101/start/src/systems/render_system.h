#pragma once
#include "../config.h"

class RenderSystem {
public:

    RenderSystem(std::vector<unsigned int>& shaders, 
        unsigned int colorbuffer);
    ~RenderSystem();
    
    void update();
    
private:

    std::vector<unsigned int>& shaders;

    unsigned int VAO, colorbuffer;

};