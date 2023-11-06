#include "texture_factory.h"

unsigned int TextureFactory::build_colorbuffer(GLFWwindow* window) {

    int width, height;
    glfwGetFramebufferSize(window, &width, &height);

    unsigned int colorbuffer;
    glGenTextures(1, &colorbuffer);
    glBindTexture(GL_TEXTURE_2D, colorbuffer);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexStorage2D(GL_TEXTURE_2D, 1, GL_RGBA32F, width, height);

    return colorbuffer;
}