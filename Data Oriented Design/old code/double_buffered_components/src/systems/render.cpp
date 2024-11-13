#include "render.h"
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <glad/glad.h>

RenderSystem::RenderSystem(uint32_t shader, GLFWwindow* window, ComponentRegistry& componentRegistry):
componentRegistry(componentRegistry)
{

    this->shader = shader;
    this->window = window;

    glUseProgram(shader);
    colorLocation = glGetUniformLocation(shader, "objectColor");
}
    
void RenderSystem::update() {
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    //lines
    glBindVertexArray(componentRegistry.particleLines.VAO);
    glUniform4f(colorLocation, 1.0f, 1.0f, 1.0f, 1.0f);
    glDrawElements(GL_LINES, componentRegistry.particleLines.elementCount, GL_UNSIGNED_INT, (void*)0);

    //Points
    glBindVertexArray(componentRegistry.particlePoints.VAO);
    glUniform4f(colorLocation, 1.0f, 0.0f, 0.0f, 1.0f);
    glDrawElements(GL_POINTS, componentRegistry.particlePoints.elementCount, GL_UNSIGNED_INT, (void*)0);
    
    glfwSwapBuffers(window);
}