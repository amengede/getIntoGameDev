#pragma once
#include "../config.h"

#include "../components/animation_component.h"
#include "../components/camera_component.h"
#include "../components/physics_component.h"
#include "../components/render_component.h"
#include "../components/transform_component.h"
#include "../components/component_set.h"

#include "../systems/animation_system.h"
#include "../systems/camera_system.h"
#include "../systems/motion_system.h"
#include "../systems/render_system.h"

#include "../view/shader.h"

class App {
public:
    App();
    ~App();
    void run();
    void set_up_opengl();
    void make_systems();

    //Components
    ComponentSet<AnimationComponent> animationComponents;
    ComponentSet<TransformComponent> transformComponents;
    ComponentSet<PhysicsComponent> physicsComponents;
    CameraComponent* cameraComponent;
    unsigned int cameraID;
    ComponentSet<RenderComponent> renderComponents;
    
private:
    void set_up_glfw();
    void handle_frame_timing();

    GLFWwindow* window;

    std::vector<unsigned int> shaders;

    //Systems
    AnimationSystem* animationSystem;
    MotionSystem* motionSystem;
    CameraSystem* cameraSystem;
    RenderSystem* renderSystem;

    //Timing
    double lastTime, currentTime;
	int numFrames;
	float frameTime;
};