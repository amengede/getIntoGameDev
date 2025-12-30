#include "render_system.h"

RenderSystem::RenderSystem(std::vector<unsigned int>& shaders, 
    GLFWwindow* window, ComponentSet<TransformComponent> &transforms,
    ComponentSet<RenderComponent> &renderables, ComponentSet<Skeleton>& skeletons):
shaders(shaders),
transforms(transforms),
renderables(renderables),
skeletons(skeletons) {
    
    this->window = window;

    build_models();

    unsigned int shader = shaders[0];
    glUseProgram(shader);

    modelLocation = glGetUniformLocation(shader, "model");
    
    boneLocations.push_back(glGetUniformLocation(shader, "boneTransforms[0]"));
    boneLocations.push_back(glGetUniformLocation(shader, "boneTransforms[1]"));
    boneLocations.push_back(glGetUniformLocation(shader, "boneTransforms[2]"));
    boneLocations.push_back(glGetUniformLocation(shader, "boneTransforms[3]"));
    boneLocations.push_back(glGetUniformLocation(shader, "boneTransforms[4]"));
}

RenderSystem::~RenderSystem() {

    //Delete Cube Model
    glDeleteVertexArrays(1, &legModel.VAO);
    glDeleteBuffers(1, &legModel.VBO);
    glDeleteBuffers(1, &legModel.EBO);
}

void RenderSystem::build_models() {

    MeshFactory meshFactory;
    legModel = meshFactory.make_skeleton();
    
}
    
void RenderSystem::update() {
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    
    for (size_t i = 0; i < renderables.entities.size(); ++i) {

        uint32_t entity = renderables.entities[i];
        RenderComponent& renderable = renderables.components[i];
        TransformComponent& transform = transforms.get_component(entity);

        if (renderable.objectType == ObjectType::eLegs) {

            //Draw the mesh
            unsigned int shader = shaders[0];
            glUseProgram(shader);
            glBindVertexArray(legModel.VAO);

            //Upload dem bonez
            Skeleton& skeleton = skeletons.get_component(entity);
            for (size_t j = 0; j < skeleton.bones.size(); ++j) {
                BoneComponent& bone = skeleton.bones[j];
                glUniformMatrix4fv(
                    boneLocations[j], 1, GL_FALSE,
                    glm::value_ptr(bone.transform));
            }

            glm::quat rotation = glm::angleAxis(glm::radians(transform.eulers.x), glm::vec3(1.0f, 0.0f, 0.0f));
            rotation = glm::angleAxis(glm::radians(transform.eulers.y), glm::vec3(0.0f, 1.0f, 0.0f)) * rotation;
            rotation = glm::angleAxis(glm::radians(transform.eulers.z), glm::vec3(0.0f, 0.0f, 1.0f)) * rotation;

            glm::mat4 translation = glm::translate(glm::mat4(1.0f), transform.position);

            glm::mat4 modelToWorld = translation * glm::mat4_cast(rotation);

            glUniformMatrix4fv(
                modelLocation, 1, GL_FALSE,
                glm::value_ptr(modelToWorld));
            glDrawElements(
                GL_LINES, legModel.elementCount,
                GL_UNSIGNED_SHORT, (void*)(0));

            //Draw the bonez
            shader = shaders[1];
            glUseProgram(shader);

            //Upload dem bonez
            for (size_t j = 0; j < skeleton.bones.size(); ++j) {
                BoneComponent& bone = skeleton.bones[j];
                glm::vec3 transformedPos = glm::vec3(modelToWorld * bone.transform * glm::vec4(bone.position, 1.0f));
                glUniform3fv(
                    positionLocation, 1,
                    glm::value_ptr(transformedPos));
                glDrawArrays(GL_POINTS, 0, 1);
            }
        }
    }

	glfwSwapBuffers(window);
}