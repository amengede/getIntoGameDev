#pragma once
#include "../config.h"

#include "../components/registry.h"

#include "../factories/factory.h"

#include "../systems/world.h"
#include "../systems/render.h"
#include "../systems/input.h"
#include "../systems/camera.h"
#include <glad/glad.h>

class App {
public:
    App();
    ~App();
    void run();
    void set_up_opengl();
    void make_systems();

    //Components
    ComponentRegistry componentRegistry;
    uint32_t shader;
    
private:
    void set_up_glfw();
    void handle_frame_timing();
    void make_objects();

    void handle_controls();

    GLFWwindow* window;

    Factory* factory;

    RenderSystem* renderSystem;
    InputSystem* inputSystem;
    World* world;
    CameraSystem* cameraSystem;

    double lastTime, currentTime, lastFrameTime;
	int numFrames;
	float frameTime = 0.0f;
};