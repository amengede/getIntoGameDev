#include "pin_system.h"

PinSystem::PinSystem(GLFWwindow* window, PinComponent& pin):
    pin(pin) {
    this->window = window;

    glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_NORMAL);

    glfwGetFramebufferSize(window, &screenWidth, &screenHeight);

    glfwSetWindowUserPointer(window, this);
    auto func = [](GLFWwindow* w, int button, int action, int mods)
        {
            static_cast<PinSystem*>(glfwGetWindowUserPointer(w))->click_callback(w, button, action, mods);
        };
    glfwSetMouseButtonCallback(window, func);

}

void PinSystem::update(float dt) {

    theta += 10.0f * dt;
    if (theta > 360) {
        theta -= 360;
    }

    glm::quat rotation = glm::quat(glm::vec3(0.0f, 0.0f, glm::radians(theta)));

    pin.localTransform = glm::mat4_cast(rotation);
}

void PinSystem::click_callback(GLFWwindow* window, int button, int action, int mods) {

    if (button != GLFW_MOUSE_BUTTON_LEFT || action != GLFW_RELEASE) {
        return;
    }

    double x_pos, y_pos;
    glfwGetCursorPos(window, &x_pos, &y_pos);

    x_pos = (x_pos - screenWidth / 2.0) / (screenWidth / 2.0);
    y_pos = -(y_pos - screenHeight / 2.0) / (screenHeight / 2.0);

    pin.position = glm::vec3(static_cast<float>(x_pos), static_cast<float>(y_pos), 0.0f);
    pin.modelToPin = glm::translate(glm::mat4(1.0f), -pin.position);
    pin.pinToModel = glm::translate(glm::mat4(1.0f), pin.position);
}