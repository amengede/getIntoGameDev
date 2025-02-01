#pragma once
#include "../config.h"
#include "../components/components.h"
#include "../components/component_set.h"
#include "../factories/model_factory.h"

class RenderSystem {
public:

    RenderSystem(std::vector<unsigned int>& shaders, GLFWwindow* window, 
        ComponentSet<TransformComponent> &transforms,
        ComponentSet<RenderComponent> &renderables, ComponentSet<Skeleton>& skeletons);
    ~RenderSystem();
    
    void update();
    
private:

    void build_models();

    std::vector<unsigned int>& shaders;

    StaticMesh legModel;
    GLFWwindow* window;

    ComponentSet<TransformComponent> &transforms;
    ComponentSet<RenderComponent> &renderables;
    ComponentSet<Skeleton>& skeletons;

    unsigned int modelLocation;
    std::vector<unsigned int> boneLocations;

    unsigned int positionLocation;
};