#include "backend/glfw_backend.h"
#include "logging/logger.h"
#include "renderer/renderer.h"
#include "controller/app.h"
#include <thread>
#include <atomic>

void spawn_render_thread(GLFWwindow* window, std::atomic<bool>* done) {
    Engine* engine = new Engine(window);

    while (!*done) {
        engine->draw();
        engine->update_timing();
    }

    delete engine;
}

int main() {
    Logger* logger = Logger::get_logger();
    logger->set_mode(true);

    int width = 800, height = 600;
    GLFWwindow* window = build_window(width, height, "ID Tech 12");

    std::atomic<bool> done = false;
    std::thread render_thread(spawn_render_thread, window, &done);
    App* app = new App(window);

    done = true;
    render_thread.join();
    glfwTerminate();
    return 0;
}