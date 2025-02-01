#pragma once
#include "../config.h"
#include "../components/components.h"

class PinSystem {
public:

    PinSystem(
        GLFWwindow* window,
        PinComponent& pin);

    void click_callback(GLFWwindow* window, int button, int action, int mods);

    void update(float dt);

private:
    GLFWwindow* window;
    PinComponent& pin;
    float theta = 0.0f;
    int screenWidth, screenHeight;
};