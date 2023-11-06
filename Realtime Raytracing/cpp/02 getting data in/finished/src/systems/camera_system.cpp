#include "camera_system.h"

CameraSystem::CameraSystem(std::vector<unsigned int>& shaders, 
    GLFWwindow* window,
    ComponentSet<CameraComponent>& cameras):
shaders(shaders),
cameras(cameras) {
    this->window = window;

    unsigned int shader = shaders[1];
    glUseProgram(shader);
    forwardsLocation = glGetUniformLocation(shader, "forwards");
    rightLocation = glGetUniformLocation(shader, "right");
    upLocation = glGetUniformLocation(shader, "up");
    posLocation = glGetUniformLocation(shader, "cameraPos");
}

bool CameraSystem::update(float dt) {

    CameraComponent& camera = cameras.components[0];

    glm::vec3& pos = camera.position;
    glm::vec3& eulers = camera.eulers;
    float theta = glm::radians(eulers.z);
    float phi = glm::radians(eulers.y);

    glm::vec3& right = camera.right;
    glm::vec3& up = camera.up;
    glm::vec3& forwards = camera.forwards;

    forwards = {
        glm::cos(theta) * glm::cos(phi),
        glm::sin(theta) * glm::cos(phi),
        glm::sin(phi)
    };
    right = glm::normalize(glm::cross(forwards, global_up));
    up = glm::normalize(glm::cross(right, forwards));

    //Keys
    glm::vec3 dPos = {0.0f, 0.0f, 0.0f};
    if (glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS) {
        dPos.x += 1.0f;
    }
    if (glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS) {
        dPos.y -= 1.0f;
    }
    if (glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS) {
        dPos.x -= 1.0f;
    }
    if (glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS) {
        dPos.y += 1.0f;
    }
    if (glm::length(dPos) > 0.1f) {
        dPos = glm::normalize(dPos);
        pos += 1.0f * dt * dPos.x * forwards;
        pos += 1.0f * dt * dPos.y * right;
    }

    if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS) {
        return true;
    }

    //Mouse
    glm::vec3 dEulers = {0.0f, 0.0f, 0.0f};
    double mouse_x, mouse_y;
    glfwGetCursorPos(window, &mouse_x, &mouse_y);
    glfwSetCursorPos(window, 320.0, 240.0);
    glfwPollEvents();

    dEulers.z = -0.1f * static_cast<float>(mouse_x - 320.0);
    dEulers.y = -0.1f * static_cast<float>(mouse_y - 240.0);

    eulers.y = fminf(89.0f, fmaxf(-89.0f, eulers.y + dEulers.y));

    eulers.z += dEulers.z;
    if (eulers.z > 360) {
        eulers.z -= 360;
    }
    else if (eulers.z < 0) {
        eulers.z += 360;
    }

    //Update camera data for raytracer
    unsigned int shader = shaders[1];
    glUseProgram(shader);
    glUniform3fv(forwardsLocation, 1, glm::value_ptr(forwards));
    glUniform3fv(rightLocation, 1, glm::value_ptr(right));
    glUniform3fv(upLocation, 1, glm::value_ptr(up));
    glUniform3fv(posLocation, 1, glm::value_ptr(pos));

    return false;
}