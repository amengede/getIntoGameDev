#include "sphere_system.h"

SphereSystem::SphereSystem(std::vector<unsigned int>& shaders,
    ComponentSet<SphereComponent>& sphereComponents):
shaders(shaders),
sphereComponents(sphereComponents) {

    glUseProgram(shaders[1]);
    sphereCountLocation = glGetUniformLocation(shaders[1], "sphereCount");
    sphereBuffer = new Buffer<SphereComponent>(0, 1);
    int sphereCount = sphereComponents.components.size();
    glUniform1i(sphereCountLocation, sphereCount);
    sphereBuffer->blit(sphereComponents.components);
    sphereBuffer->read_from();
}

SphereSystem::~SphereSystem() {
    delete sphereBuffer;
}