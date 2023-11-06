#pragma once
#include "../config.h"
#include "../backend/buffer.h"
#include "../components/sphere_component.h"
#include "../components/component_set.h"

class SphereSystem {
public:

    SphereSystem(std::vector<unsigned int>& shaders, 
        ComponentSet<SphereComponent>& sphereComponents);
    ~SphereSystem();
    
private:

    std::vector<unsigned int>& shaders;

    Buffer<SphereComponent>* sphereBuffer;
    ComponentSet<SphereComponent>& sphereComponents;
    unsigned int sphereCountLocation;

};