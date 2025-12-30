#pragma once
#include "../config.h"
#include "../components/transform_component.h"
#include "../components/render_component.h"
#include "../components/animation_component.h"
#include "../components/component_set.h"

class RenderSystem {
public:

    RenderSystem(std::vector<unsigned int>& shaders, GLFWwindow* window);
    ~RenderSystem();
    
    void update(
        ComponentSet<TransformComponent> &transformComponents,
        ComponentSet<RenderComponent> &renderComponents,
        ComponentSet<AnimationComponent> &animationComponents);
    
private:

    void build_models();
    void build_geometry();

    std::vector<unsigned int>& shaders;

    std::vector<unsigned int> VAOs;
    std::vector<unsigned int> VBOs;
    std::vector<unsigned int> EBOs;
    std::unordered_map<ObjectType, unsigned int> elementCounts;
    std::unordered_map<ObjectType, 
        std::unordered_map<AnimationType, unsigned int>> offsets;
    std::vector<unsigned int> textures;
    unsigned int modelLocation;
    GLFWwindow* window;
};