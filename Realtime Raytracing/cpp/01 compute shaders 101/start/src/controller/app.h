#pragma once
#include "../config.h"

#include "../components/camera_component.h"
#include "../components/component_set.h"

#include "../systems/camera_system.h"
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
    ComponentSet<CameraComponent> cameraComponents;
    
private:
    void set_up_glfw();
    void handle_frame_timing();

    GLFWwindow* window;

    std::vector<unsigned int> shaders;
    unsigned int colorbuffer;

    //Systems
    CameraSystem* cameraSystem;
    RenderSystem* renderSystem;

    //Timing
    double lastTime, currentTime;
	int numFrames;
	float frameTime;
};