#include "render.h"
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <glad/glad.h>

RenderSystem::RenderSystem(uint32_t shader, GLFWwindow* window, ComponentRegistry& componentRegistry):
componentRegistry(componentRegistry)
{

    this->shader = shader;
    this->window = window;

    build_models();

    glUseProgram(shader);
    modelLocation = glGetUniformLocation(shader, "model");
}

RenderSystem::~RenderSystem() {

    for (std::pair<ObjectType, Mesh> item : meshes) {
        Mesh model = item.second;
        glDeleteVertexArrays(1, &model.VAO);
        glDeleteBuffers(1, &model.VBO);
        glDeleteTextures(1, &model.material);
    }
}

void RenderSystem::build_models() {

    MeshFactory meshFactory;
    for (int i = 0; i < objectTypeCount; ++i) {
        meshes[static_cast<ObjectType>(i)] = meshFactory.make_mesh(i);
    }
}
    
void RenderSystem::update() {
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    for (size_t i = 0; i < componentRegistry.renderables.entities.size(); ++i) {
        uint32_t& id = componentRegistry.renderables.entities[i];
        RenderComponent& object = componentRegistry.renderables.components[i];
        TransformComponent& transform = componentRegistry.transforms.get_component(id);
        Mesh& mesh = meshes[object.objectType];

        glBindTexture(GL_TEXTURE_2D_ARRAY, mesh.material);
        glBindVertexArray(mesh.VAO);
        glUniformMatrix4fv(modelLocation, 1, GL_FALSE, glm::value_ptr(build_model_transform(transform)));
        glDrawElements(GL_TRIANGLES, mesh.elementCount, GL_UNSIGNED_INT, (void*) 0);
    }
    
    glfwSwapBuffers(window);
}

glm::mat4 RenderSystem::build_model_transform(TransformComponent& transform) {

    float& scale = transform.scale;

    glm::mat4 scale_and_flip = glm::scale(glm::mat4(1.0f), glm::vec3(scale));
    glm::mat4 translate = glm::translate(glm::mat4(1.0f), transform.position);
    glm::mat4 rotate_y = glm::rotate(glm::mat4(1.0f), glm::radians(transform.eulers.y), glm::vec3(0.0f, 1.0f, 0.0f));
    glm::mat4 rotate_z = glm::rotate(glm::mat4(1.0f), glm::radians(transform.eulers.z), glm::vec3(0.0f, 0.0f, 1.0f));
    return translate * rotate_z * rotate_y * scale_and_flip;
}