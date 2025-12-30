#include "render_system.h"

RenderSystem::RenderSystem(std::vector<unsigned int>& shaders,
    GLFWwindow* window,
    unsigned int colorbuffer):
shaders(shaders),
colorbuffer(colorbuffer) {

    glGenVertexArrays(1, &VAO);
    glBindVertexArray(VAO);

    int w,h;
    glfwGetFramebufferSize(window, &w, &h);
    workgroup_count_x = (w + 7) / 8;
    workgroup_count_y = (h + 7) / 8; //quick ceiling calculation
    
}

RenderSystem::~RenderSystem() {

    glDeleteVertexArrays(1, &VAO);
}
    
void RenderSystem::update() {

    //Raytrace
    glUseProgram(shaders[1]);
    glBindImageTexture(0, colorbuffer, 0, GL_FALSE, 0, GL_WRITE_ONLY, GL_RGBA32F);
    glDispatchCompute(workgroup_count_x, workgroup_count_y, 1);
    glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT);

    //Screen
    glUseProgram(shaders[0]); 
    glBindTexture(GL_TEXTURE_2D, colorbuffer);
    glDrawArrays(GL_TRIANGLES, 0, 6);

}