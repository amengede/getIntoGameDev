#include "render_system.h"

RenderSystem::RenderSystem(std::vector<unsigned int>& shaders,
    unsigned int colorbuffer):
shaders(shaders),
colorbuffer(colorbuffer) {

    glGenVertexArrays(1, &VAO);
    glBindVertexArray(VAO);
    
}

RenderSystem::~RenderSystem() {

    glDeleteVertexArrays(1, &VAO);
}
    
void RenderSystem::update() {

    //Screen
    glUseProgram(shaders[0]); 
    glBindTexture(GL_TEXTURE_2D, colorbuffer);
    glDrawArrays(GL_TRIANGLES, 0, 6);

}