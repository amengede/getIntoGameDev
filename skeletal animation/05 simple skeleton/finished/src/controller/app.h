#pragma once
#include "../config.h"

#include "../components/components.h"
#include "../components/component_set.h"

#include "../systems/render_system.h"
#include "../systems/skeletal_system.h"
#include "../systems/animation_system.h"

#include "../view/shader.h"

class App {
public:
    App();
    ~App();
    void run();
    void set_up_opengl();
    void make_systems();

    //Components
    ComponentSet<TransformComponent> transformComponents;
    ComponentSet<RenderComponent> renderComponents;
    ComponentSet<Skeleton> skeletons;
    Animations animationSet;
    ComponentSet<Animation> animations;
    
private:
    void set_up_glfw();
    void handle_frame_timing();

    GLFWwindow* window;

    std::vector<unsigned int> shaders;

    //Systems
    AnimationSystem* animationSystem;
    SkeletalSystem* skeletalSystem;
    RenderSystem* renderSystem;

    //Timing
    double lastTime, currentTime;
	int numFrames;
	float frameTime;
};