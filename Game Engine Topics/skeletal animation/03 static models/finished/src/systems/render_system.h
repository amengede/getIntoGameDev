#pragma once
#include "../config.h"
#include "../components/transform_component.h"
#include "../components/render_component.h"
#include "../components/component_set.h"
#include "../factories/model_factory.h"

class RenderSystem {
public:

    RenderSystem(std::vector<unsigned int>& shaders, GLFWwindow* window, 
        ComponentSet<TransformComponent> &transforms,
        ComponentSet<RenderComponent> &renderables);
    ~RenderSystem();
    
    void update();
    
private:

    void build_models();

    std::vector<unsigned int>& shaders;

    StaticMesh cubeModel;
    GLFWwindow* window;

    ComponentSet<TransformComponent> &transforms;
    ComponentSet<RenderComponent> &renderables;

    unsigned int modelLocation;

};