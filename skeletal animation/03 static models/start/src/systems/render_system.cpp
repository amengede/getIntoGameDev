#include "render_system.h"

RenderSystem::RenderSystem(std::vector<unsigned int>& shaders, 
    GLFWwindow* window, ComponentSet<TransformComponent> &transforms,
    ComponentSet<RenderComponent> &renderables):
shaders(shaders),
transforms(transforms),
renderables(renderables) {
    
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

        glm::mat4 model = glm::mat4(1.0f);
	    model = glm::translate(model, transform.position);
        model = glm::rotate(
            model, glm::radians(transform.eulers.x),
            { 1.0f, 0.0f, 0.0f });
        model = glm::rotate(
            model, glm::radians(transform.eulers.y),
            { 0.0f, 1.0f, 0.0f });
        model = glm::rotate(
            model, glm::radians(transform.eulers.z),
            { 0.0f, 0.0f, 1.0f });
        glUniformMatrix4fv(
		    modelLocation, 1, GL_FALSE, 
		    glm::value_ptr(model));
        glDrawElements(
            GL_TRIANGLES, cubeModel.elementCount, 
            GL_UNSIGNED_SHORT, (void*)(0));
    }

	glfwSwapBuffers(window);
}