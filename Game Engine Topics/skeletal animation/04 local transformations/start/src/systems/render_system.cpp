#include "render_system.h"

RenderSystem::RenderSystem(std::vector<unsigned int>& shaders, 
    GLFWwindow* window, ComponentSet<TransformComponent> &transforms,
    ComponentSet<RenderComponent> &renderables, PinComponent& pin):
shaders(shaders),
transforms(transforms),
renderables(renderables),
pin(pin) {
    
    this->window = window;

    build_models();

    glUseProgram(shaders[0]);
    modelLocation = glGetUniformLocation(shaders[0], "model");
    
}

RenderSystem::~RenderSystem() {

    //Delete Cube Model
    glDeleteVertexArrays(1, &cubeModel.VAO);
    glDeleteBuffers(1, &cubeModel.VBO);
    glDeleteBuffers(1, &cubeModel.EBO);
    glDeleteTextures(1, &cubeModel.material);
}

void RenderSystem::build_models() {

    MeshFactory meshFactory;
    cubeModel = meshFactory.build_gltf_mesh("cube");
    
}
    
void RenderSystem::update() {
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    
    glUseProgram(shaders[0]);
    glActiveTexture(GL_TEXTURE0);
    glBindTexture(GL_TEXTURE_2D, cubeModel.material);
    glBindVertexArray(cubeModel.VAO);
    for (size_t i = 0; i < renderables.entities.size(); ++i) {

        uint32_t entity = renderables.entities[i];
        RenderComponent& renderable = renderables.components[i];
        TransformComponent& transform = transforms.get_component(entity);

        glm::quat rotation = glm::angleAxis(glm::radians(transform.eulers.x), glm::vec3(1.0f, 0.0f, 0.0f));
        rotation = glm::angleAxis(glm::radians(transform.eulers.y), glm::vec3(0.0f, 1.0f, 0.0f)) * rotation;
        rotation = glm::angleAxis(glm::radians(transform.eulers.z), glm::vec3(0.0f, 0.0f, 1.0f)) * rotation;

        glm::mat4 translation = glm::translate(glm::mat4(1.0f), transform.position);

        glm::mat4 modelToWorld = translation * glm::mat4_cast(rotation);
        
        //incorporate pin transform

        glUniformMatrix4fv(
		    modelLocation, 1, GL_FALSE, 
		    glm::value_ptr(modelToWorld));
        glDrawElements(
            GL_TRIANGLES, cubeModel.elementCount, 
            GL_UNSIGNED_SHORT, (void*)(0));
    }

	glfwSwapBuffers(window);
}